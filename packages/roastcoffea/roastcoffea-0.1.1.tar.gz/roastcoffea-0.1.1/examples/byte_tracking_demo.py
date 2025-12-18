"""Demonstration of byte tracking and throughput visualization.

This example shows:
1. Using @track_metrics decorator to automatically track bytes read per chunk
2. Using track_bytes() context manager for fine-grained byte tracking
3. Generating throughput timeline plots

Note: Requires coffea branch with filesource exposure:
    git+https://github.com/MoAly98/coffea.git@feat/fobj_in_procmeta
"""

from __future__ import annotations

from pathlib import Path

from coffea import processor
from dask.distributed import Client, LocalCluster

from roastcoffea import (
    MetricsCollector,
    track_bytes,
    track_metrics,
    track_time,
)

from roastcoffea.visualization.plots import (
    plot_throughput_timeline,
)


class ByteTrackingProcessor(processor.ProcessorABC):
    """Demo processor with byte tracking."""

    @track_metrics
    def process(self, events):
        """Process events with byte and timing tracking."""

        print("\n", events.metadata)
        # Track jet loading specifically
        with track_bytes(self, events, "jet_loading"):
            with track_time(self, "jet_selection"):
                jets = events.Jet
                selected_jets = jets[jets.pt > 30]

        # Track muon loading
        with track_bytes(self, events, "muon_loading"):
            with track_time(self, "muon_selection"):
                muons = events.Muon
                selected_muons = muons[muons.pt > 20]

        # Compute results
        njets = len(selected_jets)
        nmuons = len(selected_muons)

        return {
            "nevents": len(events),
            "njets": njets,
            "nmuons": nmuons,
        }

    def postprocess(self, accumulator):
        return accumulator


def main():
    """Run demo workflow with byte tracking."""

    # Example fileset (replace with your files)
    fileset = {
        "ttbar": {
            "files": {
                "root://eospublic.cern.ch//eos/opendata/cms/mc/RunIISummer20UL16NanoAODv9/ZprimeToTT_M2000_W20_TuneCP2_PSweights_13TeV-madgraph-pythiaMLM-pythia8/NANOAODSIM/106X_mcRun2_asymptotic_v17-v1/270000/22BAB5D2-9E3F-E440-AB30-AE6DBFDF6C83.root": "Events",
                # Add more files here
            }
        }
    }

    # Setup Dask cluster
    cluster = LocalCluster(n_workers=4, threads_per_worker=1, processes=True)
    client = Client(cluster)

    print("Dask Dashboard:", client.dashboard_link)
    print()

    # Create processor instance
    proc = ByteTrackingProcessor()

    # Run with metrics collection
    output_dir = Path("benchmark_results")
    output_dir.mkdir(exist_ok=True)

    print("Running workflow with byte tracking...")
    print()

    with MetricsCollector(
        client, processor_instance=proc
    ) as collector:
        # Run processor
        executor = processor.DaskExecutor(client=client)
        runner = processor.Runner(executor=executor, savemetrics=True, chunksize=1000)

        output, report = runner(
            fileset,
            treename="Events",
            processor_instance=proc,
        )

        # Extract chunk metrics from output
        collector.extract_metrics_from_output(output)

        # Set coffea report
        collector.set_coffea_report(report)

    # Get metrics
    metrics = collector.metrics

    print(report, "\n\n", metrics)

    print("=" * 80)
    print("METRICS SUMMARY")
    print("=" * 80)
    print(f"Total events processed: {metrics.get('total_events', 0):,}")
    print(f"Total bytes read (Coffea): {metrics.get('total_bytes_read', 0) / 1e9:.2f} GB")
    print(f"Data throughput: {metrics.get('data_rate_gbps', 0):.2f} Gbps")
    print(f"Elapsed time: {metrics.get('elapsed_time_seconds', 0):.2f}s")
    print()

    # Check if chunk_info is available
    if "chunk_info" in metrics and metrics["chunk_info"]:
        print("✓ Chunk-level byte tracking is available!")
        print(f"  Tracked {len(metrics['chunk_info'])} chunks")
        print()

        # Generate throughput timeline plot
        print("Generating throughput timeline plot...")
        fig, ax = plot_throughput_timeline(
            chunk_info=metrics["chunk_info"],
            tracking_data=metrics.get("tracking_data"),
            output_path=output_dir / "throughput_timeline.png",
            title="Data Throughput Over Time",
        )
        print(f"  Saved to: {output_dir}/throughput_timeline.png")
        print()

        # Show per-chunk stats
        print("Per-Chunk Statistics:")
        print(f"{'Chunk':<40} {'Time (s)':<12} {'Bytes (KB)':<12} {'Rate (Mbps)':<12}")
        print("-" * 80)

        for i, ((filename, start, stop), (t0, t1, bytes_read)) in enumerate(
            list(metrics["chunk_info"].items())[:10]  # Show first 10
        ):
            duration = t1 - t0
            rate_mbps = (bytes_read * 8 / 1e6 / duration) if duration > 0 else 0
            chunk_name = f"{Path(filename).name}[{start}:{stop}]"
            print(
                f"{chunk_name:<40} {duration:<12.3f} {bytes_read/1e3:<12.1f} {rate_mbps:<12.2f}"
            )

        if len(metrics["chunk_info"]) > 10:
            print(f"... and {len(metrics['chunk_info']) - 10} more chunks")
    else:
        print("⚠ No chunk_info available")

    # Show fine-grained byte tracking if available
    if "raw_chunk_metrics" in metrics:
        print()
        print("Fine-Grained Byte Tracking:")
        print(f"{'Section':<20} {'Total Bytes (KB)':<20} {'Chunks':<10}")
        print("-" * 50)

        # Aggregate bytes by section across all chunks
        section_totals = {}
        for chunk in metrics["raw_chunk_metrics"]:
            if "bytes" in chunk:
                for section, bytes_count in chunk["bytes"].items():
                    if section not in section_totals:
                        section_totals[section] = {"total": 0, "count": 0}
                    section_totals[section]["total"] += bytes_count
                    section_totals[section]["count"] += 1

        for section, data in sorted(
            section_totals.items(), key=lambda x: x[1]["total"], reverse=True
        ):
            print(
                f"{section:<20} {data['total']/1e3:<20.1f} {data['count']:<10}"
            )

    print()
    print("=" * 80)
    print("Demo complete!")
    print("=" * 80)

    client.close()
    cluster.close()


if __name__ == "__main__":
    main()
