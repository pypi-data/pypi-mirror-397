// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

use anyhow::{ensure, Result};
use dashmap::DashSet;
use dsi_progress_logger::{concurrent_progress_logger, progress_logger, ProgressLog};
use epserde::Epserde;
use rayon::prelude::*;
use rdst::RadixSort;
use sux::bits::BitFieldVec;
use sux::bits::BitVec;
use sux::dict::elias_fano::{EliasFano, EliasFanoBuilder, EliasFanoConcurrentBuilder};
use sux::prelude::{SelectAdaptConst, SelectZeroAdaptConst};
use sux::traits::IndexedSeq;
use swh_graph::graph::{
    NodeId, SwhBackwardGraph, SwhForwardGraph, SwhGraph, SwhGraphWithProperties,
};
use swh_graph::views::contiguous_subgraph::{
    ContiguousSubgraph, Contraction, MonotoneContractionBackend,
};
use value_traits::slices::SliceByValue;
use webgraph::traits::labels::SortedIterator;

type EfSeqDict<D> =
    EliasFano<SelectZeroAdaptConst<SelectAdaptConst<BitVec<D>, D, 12, 3>, D, 12, 3>>;
type EfSeq<D> = EliasFano<SelectAdaptConst<sux::bits::BitVec<D>, D, 12, 3>>;

/// A structure that gives access to connected components of a subgraph.
#[derive(Epserde)]
pub struct SubgraphWccs<
    D: AsRef<[usize]> = Box<[usize]>,
    V: SliceByValue<Value = usize> = BitFieldVec<usize>,
> {
    num_components: usize,
    /// To be interpreted as wrapped in [`Contraction`]
    contraction: EfSeqDict<D>,
    ccs: V,
    component_sizes: Option<EfSeq<D>>,
}

impl SubgraphWccs<Box<[usize]>, BitFieldVec<usize>> {
    /// Given a set of nodes, computes the connected components in the whole graph
    /// that contain these nodes.
    ///
    /// For example, if a graph is:
    ///
    /// ```ignore
    /// A -> B -> C
    ///      ^
    ///     /
    /// D --
    /// E -> F -> G
    /// ```
    ///
    /// then:
    ///
    /// * `build_from_closure([A, D, F])` and `build_from_closure([A, B, D, F])` compute
    ///   `[[A, B, C, D], [E, F, G]]`
    /// * `build_from_closure([A])` computes `[[A, B, C, D]]`
    pub fn build_from_closure<G, I: IntoParallelIterator<Item = NodeId>>(
        graph: G,
        nodes: I,
        sort_by_size: bool,
    ) -> Result<Self>
    where
        // FIXME: G should not need to be 'static
        G: SwhForwardGraph + SwhBackwardGraph + SwhGraphWithProperties + Sync + Send + 'static,
        for<'succ> <<G as SwhForwardGraph>::Successors<'succ> as IntoIterator>::IntoIter:
            SortedIterator,
        for<'pred> <<G as SwhBackwardGraph>::Predecessors<'pred> as IntoIterator>::IntoIter:
            SortedIterator,
    {
        let seen = DashSet::new(); // shared between DFSs to avoid duplicate work

        let mut pl = concurrent_progress_logger! {
            item_name = "node",
            local_speed = true,
            display_memory = true,
        };
        pl.start("Listing nodes in connected closure");
        nodes
            .into_par_iter()
            .for_each_with(pl.clone(), |pl, start_node| {
                seen.insert(start_node);
                let mut todo = vec![start_node];

                while let Some(node) = todo.pop() {
                    pl.light_update();
                    for pred in graph.predecessors(node) {
                        let new = seen.insert(pred);
                        if new {
                            todo.push(pred);
                        }
                    }
                    for succ in graph.successors(node) {
                        let new = seen.insert(succ);
                        if new {
                            todo.push(succ);
                        }
                    }
                }
            });
        pl.done();

        let nodes: Vec<_> = seen.into_par_iter().collect();
        Self::build_from_nodes(graph, nodes, sort_by_size)
    }

    /// Given a set of nodes, computes the connected components in the subgraph made
    /// of only these nodes.
    ///
    /// For example, if a graph is:
    ///
    /// ```ignore
    /// A -> B -> C
    ///      ^
    ///     /
    /// D --
    /// E -> F -> G
    /// ```
    ///
    /// then:
    ///
    /// * `build_from_nodes([A, D, F])` computes `[[A], [D], [F]]`
    /// * `build_from_nodes([A, B, D, F])` compute `[[A, B, D], [F]]`
    /// * `build_from_nodes([A])` computes `[[A]]`
    pub fn build_from_nodes<G>(graph: G, mut nodes: Vec<NodeId>, sort_by_size: bool) -> Result<Self>
    where
        // FIXME: G should not need to be 'static
        G: SwhForwardGraph + SwhBackwardGraph + SwhGraphWithProperties + Sync + Send + 'static,
        for<'succ> <<G as SwhForwardGraph>::Successors<'succ> as IntoIterator>::IntoIter:
            SortedIterator,
        for<'pred> <<G as SwhBackwardGraph>::Predecessors<'pred> as IntoIterator>::IntoIter:
            SortedIterator,
    {
        log::info!("Sorting reachable nodes");
        nodes.radix_sort_unstable();

        unsafe { Self::build_from_sorted_nodes(graph, nodes, sort_by_size) }
    }

    /// Same as [`Self::build_from_nodes`] but assumes the vector of nodes is sorted.
    ///
    /// # Safety
    ///
    /// Undefined behavior if the vector is not sorted
    pub unsafe fn build_from_sorted_nodes<G>(
        graph: G,
        nodes: Vec<NodeId>,
        sort_by_size: bool,
    ) -> Result<Self>
    where
        // FIXME: G should not need to be 'static
        G: SwhForwardGraph + SwhBackwardGraph + SwhGraphWithProperties + Sync + Send + 'static,
        for<'succ> <<G as SwhForwardGraph>::Successors<'succ> as IntoIterator>::IntoIter:
            SortedIterator,
        for<'pred> <<G as SwhBackwardGraph>::Predecessors<'pred> as IntoIterator>::IntoIter:
            SortedIterator,
    {
        let mut pl = concurrent_progress_logger!(
            item_name = "node",
            local_speed = true,
            display_memory = true,
            expected_updates = Some(nodes.len()),
        );
        ensure!(!nodes.is_empty(), "Empty set of nodes"); // Makes EliasFanoConcurrentBuilder panic
        let efb = EliasFanoConcurrentBuilder::new(nodes.len(), graph.num_nodes());
        pl.start("Compressing set of reachable nodes");
        nodes
            .into_par_iter()
            .enumerate()
            // SAFETY: 'index' is unique, and the vector is sorted
            .for_each_with(pl.clone(), |pl, (index, node)| {
                pl.light_update();
                unsafe { efb.set(index, node) }
            });
        pl.done();

        let contraction = Contraction(efb.build_with_seq_and_dict());

        Self::build_from_contraction(graph, contraction, sort_by_size)
    }

    /// Same as [`Self::build_from_nodes`] but takes a [`Contraction`] as input
    /// instead of a `Vec<usize>`
    pub fn build_from_contraction<G>(
        graph: G,
        contraction: Contraction<EfSeqDict<Box<[usize]>>>,
        sort_by_size: bool,
    ) -> Result<Self>
    where
        // FIXME: G should not need to be 'static
        G: SwhForwardGraph + SwhBackwardGraph + SwhGraphWithProperties + Sync + Send + 'static,
        for<'succ> <<G as SwhForwardGraph>::Successors<'succ> as IntoIterator>::IntoIter:
            SortedIterator,
        for<'pred> <<G as SwhBackwardGraph>::Predecessors<'pred> as IntoIterator>::IntoIter:
            SortedIterator,
    {
        // only keep selected nodes
        let contracted_graph = ContiguousSubgraph::new_from_contraction(graph, contraction);

        let mut pl = concurrent_progress_logger!(
            item_name = "node",
            local_speed = true,
            display_memory = true,
            expected_updates = Some(contracted_graph.num_nodes()),
        );
        let symmetrized_graph = swh_graph::views::SymmetricWebgraphAdapter(contracted_graph);
        let mut sccs = webgraph_algo::sccs::symm_par(&symmetrized_graph, &mut pl);
        let swh_graph::views::SymmetricWebgraphAdapter(contracted_graph) = symmetrized_graph;
        pl.done();

        let component_sizes = if sort_by_size {
            log::info!("Sorting connected components by size...");
            let sizes_vec = sccs.sort_by_size();
            let mut pl = progress_logger!(
                item_name = "node",
                local_speed = true,
                display_memory = true,
                expected_updates = Some(sccs.num_components()),
            );
            pl.start("Compacting WCC sizes");
            let mut efb = EliasFanoBuilder::new(
                sccs.num_components(),
                sizes_vec.first().copied().unwrap_or(1),
            );

            // Reversed because Elias-Fano needs to be in ascending order
            efb.extend(sizes_vec.iter().rev().copied());
            Some(efb.build_with_seq())
        } else {
            None
        };

        let mut pl = progress_logger!(
            item_name = "node",
            local_speed = true,
            display_memory = true,
            expected_updates = Some(contracted_graph.num_nodes()),
        );
        pl.start("Compacting WCCs array");

        let bit_width = sccs
            .num_components()
            .next_power_of_two() // because checked_ilog2() rounds down
            .checked_ilog2()
            .unwrap()
            .max(1); // UB in BitFieldVec when bit_width = 0
        let bit_width = usize::try_from(bit_width).expect("bit width overflowed usize");
        let mut ccs = BitFieldVec::with_capacity(bit_width, contracted_graph.num_nodes());
        for node in contracted_graph.iter_nodes(pl) {
            ccs.push(
                // Reverse component ids to be consistent with component_sizes
                sccs.num_components() - sccs.components()[node] - 1,
            );
        }

        let (_graph, Contraction(contraction)) = contracted_graph.into_parts();

        Ok(Self {
            ccs,
            contraction,
            component_sizes,
            num_components: sccs.num_components(),
        })
    }
}

impl<D: AsRef<[usize]>, V: SliceByValue<Value = usize>> SubgraphWccs<D, V> {
    /// Returns the total number in all connected components
    pub fn num_nodes(&self) -> usize {
        self.contraction().num_nodes()
    }

    pub fn contraction(&self) -> Contraction<&impl MonotoneContractionBackend> {
        Contraction(&self.contraction)
    }

    /// Returns an iterator on all the nodes in any connected component
    ///
    /// Order is not guaranteed.
    ///
    /// Updates the progress logger on every node id from 0 to `self.num_nodes()`,
    /// even those that are filtered out by an underlying subgraph.
    pub fn iter_nodes(&self) -> impl Iterator<Item = NodeId> + use<'_, D, V> {
        (0..self.contraction().num_nodes()).map(|node| self.contraction().underlying_node_id(node))
    }
    /// Returns a parallel iterator on all the nodes in any connected component
    ///
    /// Order is not guaranteed.
    ///
    /// Updates the progress logger on every node id from 0 to `self.num_nodes()`,
    /// even those that are filtered out by an underlying subgraph.
    pub fn par_iter_nodes(&self) -> impl ParallelIterator<Item = NodeId> + use<'_, D, V>
    where
        D: Sync + Send,
        V: Sync + Send,
    {
        (0..self.contraction().num_nodes())
            .into_par_iter()
            .map(move |node| self.contraction().underlying_node_id(node))
    }

    /// Returns the number of strongly connected components.
    pub fn num_components(&self) -> usize {
        self.num_components
    }

    /// Given a node, returns which component it belongs to, if any
    #[inline(always)]
    pub fn component(&self, node: NodeId) -> Option<usize> {
        self.ccs
            .get_value(self.contraction().node_id_from_underlying(node)?)
    }

    /// Returns `None` if component sizes were not computed, or the size of the `i`th component
    /// otherwise
    pub fn component_size(&self, i: usize) -> Option<usize> {
        self.component_sizes.as_ref().map(move |sizes| sizes.get(i))
    }

    /// Returns `None` if component sizes were not computed, `Some(size)` otherwise
    pub fn component_sizes(&self) -> Option<impl Iterator<Item = usize> + use<'_, D, V>> {
        self.component_sizes.as_ref().map(|sizes| sizes.iter())
    }
}
