import json
import os
import threading
import typing
from collections import defaultdict

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult


class QuraiteInMemorySpanExporter(SpanExporter):
    def __init__(self) -> None:
        # self.spans: typing.List[ReadableSpan] = []
        self.traces: typing.Dict[int, typing.List[ReadableSpan]] = defaultdict(list)
        self.testcase_to_trace: typing.Dict[str, int] = {}

        self._stopped = False
        self._lock = threading.Lock()

    def handle_testcase_trace(self, span: ReadableSpan) -> None:
        """Handle a testcase trace."""
        # print(f"🟢 testcase trace received: {span.name}")
        # print(f"🟢 Span: {span.context}")
        formatted_trace_id = format(span.context.trace_id, "032x")[:8]
        # print(f"🟢 testcase formatted trace id: {formatted_trace_id}")
        self.traces[formatted_trace_id] = []
        self.testcase_to_trace[span.name] = formatted_trace_id

    def export(self, spans: typing.Sequence[ReadableSpan]) -> SpanExportResult:
        """Stores a list of spans in memory."""
        if self._stopped:
            return SpanExportResult.FAILURE

        with self._lock:
            for span in spans:
                formatted_trace_id = format(span.context.trace_id, "032x")[:8]
                # print(f"🟢 span formatted context trace id: {formatted_trace_id}")
                self.traces[formatted_trace_id].append(span)
                # self.spans.append(span)

        return SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        """Shut downs the exporter.

        Calls to export after the exporter has been shut down will fail.
        """
        print("Shutting down exporter")
        self._stopped = True

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True

    def get_traces(self) -> typing.Dict[int, typing.List[ReadableSpan]]:
        """Get all spans grouped by trace ID"""
        return dict(self.traces)

    def get_trace_by_testcase(self, testcase_name: str) -> typing.List[ReadableSpan]:
        """Get all spans for a specific testcase"""
        with self._lock:
            return self.traces.get(self.testcase_to_trace.get(testcase_name, None), [])

    def get_trace(self, trace_id: int) -> typing.List[ReadableSpan]:
        """Get all spans for a specific trace"""
        return self.traces.get(trace_id, [])

    def get_trace_count(self) -> int:
        """Get the number of unique traces"""
        return len(self.traces)

    def print_trace_summary(self):
        """Print a summary of all traces"""
        print(f"\n{'='*60}")
        print(f"Total Traces: {self.get_trace_count()}")
        for trace_id, spans in self.traces.items():
            print(f"Trace ID: {trace_id}...")
            print(f"Spans in trace: {len(spans)}")
        print(f"Total Testcases: {self.testcase_to_trace}")
        print(f"TraceIDs: {self.traces.keys()}")
        print(f"{'='*60}\n")

        # for trace_id, spans in self.traces.items():
        #     trace_id_hex = format(trace_id, '032x')
        #     print(f"📊 Trace ID: {trace_id_hex}")
        #     print(f"   Spans in trace: {len(spans)}")

        #     # Sort spans by start time to show execution order
        #     sorted_spans = sorted(spans, key=lambda s: s.start_time)

        #     for span in sorted_spans:
        #         duration_ms = (span.end_time - span.start_time) / 1e6
        #         parent_id = format(span.parent.span_id, '016x') if span.parent else "None"
        #         indent = "   " if span.parent else ""
        #         print(f"   {indent}├─ {span.name}")
        #         print(f"   {indent}   ├─ Span ID: {format(span.context.span_id, '016x')}")
        #         print(f"   {indent}   ├─ Parent ID: {parent_id}")
        #         print(f"   {indent}   ├─ Duration: {duration_ms:.2f}ms")
        #         if span.attributes:
        #             print(f"   {indent}   └─ Attributes: {dict(span.attributes)}")
        #     print()

    def save_traces_to_file(self, filename: typing.Optional[str] = "traces.json"):
        """Save a trace to a file"""
        traces = []
        for trace_id, spans in self.traces.items():
            traces.append(
                {
                    "trace_id": trace_id,
                    "spans": [json.loads(span.to_json()) for span in spans],
                }
            )

        os.makedirs(os.path.dirname(f"traces/{filename}"), exist_ok=True)
        with open(f"traces/{filename}", "w") as f:
            json.dump(traces, f, indent=2)
