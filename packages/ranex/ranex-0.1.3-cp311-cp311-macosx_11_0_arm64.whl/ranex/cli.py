import argparse
import json
import os
import sys
from importlib.metadata import version as package_version
from typing import List, Optional


def _print_json(data: object) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def _cmd_version(_: argparse.Namespace) -> int:
    print(package_version("ranex"))
    return 0


def _cmd_atlas_glob(args: argparse.Namespace) -> int:
    from ranex import Atlas

    try:
        atlas = Atlas(args.project_root)
        res = atlas.glob_python_files(args.pattern, limit=args.limit)
    except Exception as e:
        print(f"glob failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        _print_json(res)
    else:
        for path in res:
            print(path)

    return 0


def _cmd_atlas_grep_spans(args: argparse.Namespace) -> int:
    from ranex import Atlas

    try:
        atlas = Atlas(args.project_root)
        res = atlas.grep_spans(args.query, limit=args.limit, path_glob=args.path_glob)
    except Exception as e:
        print(f"grep failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        _print_json(res)
    else:
        for item in res:
            file_path = item.get("file_path", "")
            start = item.get("line_start", "")
            end = item.get("line_end", "")
            kind = item.get("kind", "")
            evidence = item.get("evidence_type", "")
            print(f"{file_path}:{start}-{end} [{evidence}] {kind}")

    return 0


def _cmd_atlas_search_spans(args: argparse.Namespace) -> int:
    from ranex import Atlas

    try:
        atlas = Atlas(args.project_root)
        res = atlas.search_spans(args.query, limit=args.limit)
    except Exception as e:
        print(f"search-spans failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        _print_json(res)
    else:
        for item in res:
            file_path = item.get("file_path", "")
            start = item.get("line_start", "")
            end = item.get("line_end", "")
            kind = item.get("kind", "")
            score = item.get("score", "")
            evidence = item.get("evidence_type", "")
            print(f"{file_path}:{start}-{end} [{evidence}] score={score} {kind}")

    return 0


def _cmd_atlas_read_span(args: argparse.Namespace) -> int:
    from ranex import Atlas

    try:
        atlas = Atlas(args.project_root)
        snippet = atlas.read_span(
            args.file_path,
            args.start_line,
            args.end_line,
            max_bytes=args.max_bytes,
        )
    except Exception as e:
        print(f"read-span failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        _print_json(
            {
                "file_path": args.file_path,
                "start_line": args.start_line,
                "end_line": args.end_line,
                "max_bytes": args.max_bytes,
                "snippet": snippet,
            }
        )
    else:
        print(snippet)

    return 0


def _cmd_atlas_fastapi_scaling_policy(args: argparse.Namespace) -> int:
    from ranex import Atlas

    try:
        atlas = Atlas(args.project_root)
        res = atlas.fastapi_scaling_policy()
    except Exception as e:
        print(f"fastapi-scaling-policy failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        _print_json(res)
    else:
        if isinstance(res, dict):
            version = res.get("version", "")
            enabled = res.get("enabled", "")
            print(f"version={version}")
            print(f"enabled={enabled}")
        else:
            print(res)

    return 0


def _cmd_atlas_fastapi_scaling_report(args: argparse.Namespace) -> int:
    from ranex import Atlas

    try:
        atlas = Atlas(args.project_root)
        res = atlas.analyze_fastapi_scaling()
    except Exception as e:
        print(f"fastapi-scaling-report failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        _print_json(res)
    else:
        if isinstance(res, dict):
            policy_version = res.get("policy_version", "")
            violations = res.get("violations", [])
            print(f"policy_version={policy_version}")
            if isinstance(violations, list):
                print(f"violations={len(violations)}")
        else:
            print(res)

    return 0


def _cmd_atlas_fastapi_router_topology(args: argparse.Namespace) -> int:
    from ranex import Atlas

    try:
        atlas = Atlas(args.project_root)
        res = atlas.analyze_fastapi_router_topology()
    except Exception as e:
        print(f"fastapi-router-topology failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        _print_json(res)
    else:
        if isinstance(res, dict):
            routers = res.get("routers", [])
            direct = res.get("direct_app_routes", [])
            if isinstance(routers, list):
                print(f"routers={len(routers)}")
            if isinstance(direct, list):
                print(f"direct_app_routes={len(direct)}")
        else:
            print(res)

    return 0


def _cmd_atlas_fastapi_truth_capsule(args: argparse.Namespace) -> int:
    from ranex import Atlas

    try:
        atlas = Atlas(args.project_root)
        res = atlas.fastapi_truth_capsule(
            method=args.method,
            path=args.path,
            operation_id=args.operation_id,
            handler_qualified_name=args.handler_qualified_name,
            mode=args.mode,
            strict=args.strict,
            max_spans=args.max_spans,
            max_dependency_depth=args.max_dependency_depth,
            max_call_depth=args.max_call_depth,
            max_call_nodes=args.max_call_nodes,
            include_snippets=args.include_snippets,
            snippet_max_lines=args.snippet_max_lines,
        )
    except Exception as e:
        print(f"fastapi-truth-capsule failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        _print_json(res)
    else:
        if isinstance(res, dict):
            capsule_id = res.get("capsule_id", "")
            resolved_by = res.get("resolved_by", "")
            is_partial = res.get("is_partial", "")
            print(f"capsule_id={capsule_id}")
            print(f"resolved_by={resolved_by}")
            print(f"is_partial={is_partial}")
        else:
            print(res)

    return 0


def _cmd_init(args: argparse.Namespace) -> int:
    from ranex.templates import FIREWALL_YAML_TEMPLATE

    project_root = os.path.abspath(args.project_root)
    ranex_dir = os.path.join(project_root, ".ranex")
    os.makedirs(ranex_dir, exist_ok=True)

    firewall_path = os.path.join(ranex_dir, "firewall.yaml")
    if os.path.exists(firewall_path) and not args.force:
        print(f"{firewall_path} already exists (use --force to overwrite)")
        return 1

    with open(firewall_path, "w", encoding="utf-8") as f:
        f.write(FIREWALL_YAML_TEMPLATE)

    print(f"Wrote {firewall_path}")
    return 0


def _cmd_atlas_scan(args: argparse.Namespace) -> int:
    from ranex import Atlas

    try:
        atlas = Atlas(args.project_root)
        res = atlas.scan()
    except Exception as e:
        print(f"scan failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        _print_json(res)
    else:
        artifacts = res.get("artifacts_found", "")
        files_scanned = res.get("files_scanned", "")
        duration_ms = res.get("duration_ms", "")
        print(f"artifacts_found={artifacts}")
        print(f"files_scanned={files_scanned}")
        print(f"duration_ms={duration_ms}")

    return 0


def _cmd_atlas_search(args: argparse.Namespace) -> int:
    from ranex import Atlas

    try:
        atlas = Atlas(args.project_root)
        res = atlas.search(args.query, limit=args.limit)
    except Exception as e:
        print(f"search failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        _print_json(res)
    else:
        for item in res:
            file_path = item.get("file_path", "")
            kind = item.get("kind", "")
            qualified_name = item.get("qualified_name", item.get("symbol_name", ""))
            line_start = item.get("line_start", "")
            print(f"{file_path}:{line_start} [{kind}] {qualified_name}")

    return 0


def _cmd_atlas_search_by_feature(args: argparse.Namespace) -> int:
    from ranex import Atlas

    try:
        atlas = Atlas(args.project_root)
        res = atlas.search_by_feature(args.feature)
    except Exception as e:
        print(f"search-by-feature failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        _print_json(res)
    else:
        for item in res:
            file_path = item.get("file_path", "")
            kind = item.get("kind", "")
            qualified_name = item.get("qualified_name", item.get("symbol_name", ""))
            line_start = item.get("line_start", "")
            print(f"{file_path}:{line_start} [{kind}] {qualified_name}")

    return 0


def _cmd_atlas_count(args: argparse.Namespace) -> int:
    from ranex import Atlas

    try:
        atlas = Atlas(args.project_root)
        res = atlas.count()
    except Exception as e:
        print(f"count failed: {e}", file=sys.stderr)
        return 1

    print(res)
    return 0


def _cmd_atlas_health(args: argparse.Namespace) -> int:
    from ranex import Atlas

    try:
        atlas = Atlas(args.project_root)
        res = atlas.health()
    except Exception as e:
        print(f"health failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        _print_json(res)
    else:
        for k in sorted(res.keys()):
            print(f"{k}={res[k]}")

    return 0


def _cmd_atlas_detect_patterns(args: argparse.Namespace) -> int:
    from ranex import Atlas

    try:
        atlas = Atlas(args.project_root)
        res = atlas.detect_patterns()
    except Exception as e:
        print(f"detect-patterns failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        _print_json(res)
    else:
        for item in res:
            pattern_type = item.get("pattern_type", "")
            name = item.get("name", "")
            file_path = item.get("file_path", "")
            confidence = item.get("confidence", "")
            print(f"{pattern_type} {name} file={file_path} confidence={confidence}")

    return 0


def _cmd_atlas_get_patterns(args: argparse.Namespace) -> int:
    from ranex import Atlas

    try:
        atlas = Atlas(args.project_root)
        res = atlas.get_patterns()
    except Exception as e:
        print(f"get-patterns failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        _print_json(res)
    else:
        for item in res:
            pattern_type = item.get("pattern_type", "")
            name = item.get("name", "")
            file_path = item.get("file_path", "")
            confidence = item.get("confidence", "")
            print(f"{pattern_type} {name} file={file_path} confidence={confidence}")

    return 0


def _cmd_atlas_analyze_function_impact(args: argparse.Namespace) -> int:
    from ranex import Atlas

    try:
        atlas = Atlas(args.project_root)
        res = atlas.analyze_function_impact(args.qualified_name)
    except Exception as e:
        print(f"analyze-function-impact failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        _print_json(res)
    else:
        for k in sorted(res.keys()):
            print(f"{k}={res[k]}")

    return 0


def _cmd_atlas_analyze_file_impact(args: argparse.Namespace) -> int:
    from ranex import Atlas

    try:
        atlas = Atlas(args.project_root)
        res = atlas.analyze_file_impact(args.file_path)
    except Exception as e:
        print(f"analyze-file-impact failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        _print_json(res)
    else:
        for k in sorted(res.keys()):
            print(f"{k}={res[k]}")

    return 0


def _cmd_atlas_get_dependencies(args: argparse.Namespace) -> int:
    from ranex import Atlas

    try:
        atlas = Atlas(args.project_root)
        res = atlas.get_dependencies(args.file_path)
    except Exception as e:
        print(f"get-dependencies failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        _print_json(res)
    else:
        for item in res:
            print(item)

    return 0


def _cmd_atlas_get_dependents(args: argparse.Namespace) -> int:
    from ranex import Atlas

    try:
        atlas = Atlas(args.project_root)
        res = atlas.get_dependents(args.file_path)
    except Exception as e:
        print(f"get-dependents failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        _print_json(res)
    else:
        for item in res:
            print(item)

    return 0


def _cmd_atlas_find_duplicates(args: argparse.Namespace) -> int:
    from ranex import Atlas

    try:
        atlas = Atlas(args.project_root)
        res = atlas.find_duplicates()
    except Exception as e:
        print(f"find-duplicates failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        _print_json(res)
    else:
        for item in res:
            a = item.get("artifact_a", "")
            b = item.get("artifact_b", "")
            similarity = item.get("similarity", "")
            match_type = item.get("match_type", "")
            print(f"{match_type} similarity={similarity} {a} <-> {b}")

    return 0


def _cmd_atlas_detect_cycles(args: argparse.Namespace) -> int:
    from ranex import Atlas

    try:
        atlas = Atlas(args.project_root)
        res = atlas.detect_cycles()
    except Exception as e:
        print(f"detect-cycles failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        _print_json(res)
    else:
        for i, cycle in enumerate(res):
            if isinstance(cycle, list):
                print(f"cycle={i} " + " -> ".join(cycle))
            else:
                print(f"cycle={i} {cycle}")

    return 0


def _cmd_firewall_check_import(args: argparse.Namespace) -> int:
    from ranex import Firewall

    fw = Firewall(args.project_root)
    res = fw.check_import(args.import_path)

    if args.json:
        _print_json(res)
        return 0 if bool(res.get("allowed")) else 2

    allowed = bool(res.get("allowed"))
    status = res.get("status", "")
    reason = res.get("reason", "")
    suggestion = res.get("suggestion", "")

    print(f"allowed={allowed} status={status}")
    if reason:
        print(f"reason={reason}")
    if suggestion:
        print(f"suggestion={suggestion}")

    return 0 if allowed else 2


def _cmd_firewall_check_imports(args: argparse.Namespace) -> int:
    from ranex import Firewall

    fw = Firewall(args.project_root)
    res = fw.check_imports(list(args.import_paths))

    if args.json:
        _print_json(res)
    else:
        for item in res:
            imp = item.get("import", "")
            allowed = bool(item.get("allowed"))
            status = item.get("status", "")
            reason = item.get("reason", "")
            print(f"import={imp} allowed={allowed} status={status} reason={reason}")

    all_allowed = all(bool(item.get("allowed")) for item in res)
    return 0 if all_allowed else 2


def _cmd_firewall_analyze_file(args: argparse.Namespace) -> int:
    from ranex import Firewall

    fw = Firewall(args.project_root)
    res = fw.analyze_file(args.file_path)

    if args.json:
        _print_json(res)
    else:
        print(f"file_path={res.get('file_path', '')}")
        print(f"imports_found={res.get('imports_found', '')}")
        print(f"passed={res.get('passed', '')}")
        violations = res.get("violations", [])
        if isinstance(violations, list):
            for v in violations:
                imp = v.get("import", "")
                line = v.get("line", "")
                status = v.get("status", "")
                reason = v.get("reason", "")
                print(f"violation: {line} import={imp} status={status} reason={reason}")

    return 0 if bool(res.get("passed")) else 2


def _cmd_firewall_typosquat(args: argparse.Namespace) -> int:
    from ranex import Firewall

    fw = Firewall(args.project_root)
    res = fw.check_typosquat(args.package_name)

    if args.json:
        _print_json(res)
    else:
        for k in sorted(res.keys()):
            print(f"{k}={res[k]}")

    return 0


def _cmd_firewall_policy_mode(args: argparse.Namespace) -> int:
    from ranex import Firewall

    fw = Firewall(args.project_root)
    print(fw.policy_mode)
    return 0


def _cmd_firewall_blocked_patterns(args: argparse.Namespace) -> int:
    from ranex import Firewall

    fw = Firewall(args.project_root)
    res = fw.get_blocked_patterns()

    if args.json:
        _print_json(res)
    else:
        for item in res:
            pattern = item.get("pattern", "")
            severity = item.get("severity", "")
            reason = item.get("reason", "")
            print(f"pattern={pattern} severity={severity} reason={reason}")

    return 0


def _cmd_firewall_policy_info(args: argparse.Namespace) -> int:
    from ranex import Firewall

    fw = Firewall(args.project_root)
    info = fw.get_policy_info()

    if args.json:
        _print_json(info)
    else:
        for k in sorted(info.keys()):
            print(f"{k}={info[k]}")

    return 0


def _cmd_firewall_list_rules(args: argparse.Namespace) -> int:
    from ranex import Firewall

    fw = Firewall(args.project_root)
    rules = fw.list_rules()

    if args.json:
        _print_json(rules)
    else:
        if not isinstance(rules, dict):
            print(rules)
            return 0

        for k in sorted(rules.keys()):
            v = rules[k]
            if isinstance(v, (list, dict)):
                print(f"{k}=")
                print(json.dumps(v, indent=2, sort_keys=True))
            else:
                print(f"{k}={v}")

    return 0


def _cmd_firewall_allowed_packages(args: argparse.Namespace) -> int:
    from ranex import Firewall

    fw = Firewall(args.project_root)
    pkgs = fw.get_allowed_packages()

    if args.json:
        _print_json(pkgs)
    else:
        for p in pkgs:
            print(p)

    return 0


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ranex")
    sub = p.add_subparsers(dest="command", required=True)

    p_version = sub.add_parser("version", help="Print ranex version")
    p_version.set_defaults(func=_cmd_version)

    p_init = sub.add_parser(
        "init",
        help="Initialize .ranex/ config in a project (writes .ranex/firewall.yaml)",
    )
    p_init.add_argument("--project-root", default=os.getcwd())
    p_init.add_argument("--force", action="store_true")
    p_init.set_defaults(func=_cmd_init)

    p_atlas = sub.add_parser("atlas", help="Atlas operations")
    atlas_sub = p_atlas.add_subparsers(dest="atlas_command", required=True)

    p_atlas_scan = atlas_sub.add_parser("scan", help="Scan and index a project")
    p_atlas_scan.add_argument("--project-root", default=os.getcwd())
    p_atlas_scan.add_argument("--json", action="store_true")
    p_atlas_scan.set_defaults(func=_cmd_atlas_scan)

    p_atlas_search = atlas_sub.add_parser("search", help="Search indexed artifacts")
    p_atlas_search.add_argument("query")
    p_atlas_search.add_argument("--project-root", default=os.getcwd())
    p_atlas_search.add_argument("--limit", type=int, default=100)
    p_atlas_search.add_argument("--json", action="store_true")
    p_atlas_search.set_defaults(func=_cmd_atlas_search)

    p_atlas_search_feature = atlas_sub.add_parser(
        "search-by-feature", help="Search indexed artifacts by feature tag"
    )
    p_atlas_search_feature.add_argument("feature")
    p_atlas_search_feature.add_argument("--project-root", default=os.getcwd())
    p_atlas_search_feature.add_argument("--json", action="store_true")
    p_atlas_search_feature.set_defaults(func=_cmd_atlas_search_by_feature)

    p_atlas_count = atlas_sub.add_parser("count", help="Count indexed artifacts")
    p_atlas_count.add_argument("--project-root", default=os.getcwd())
    p_atlas_count.set_defaults(func=_cmd_atlas_count)

    p_atlas_health = atlas_sub.add_parser("health", help="Check Atlas health/status")
    p_atlas_health.add_argument("--project-root", default=os.getcwd())
    p_atlas_health.add_argument("--json", action="store_true")
    p_atlas_health.set_defaults(func=_cmd_atlas_health)

    p_atlas_detect_patterns = atlas_sub.add_parser(
        "detect-patterns", help="Detect patterns in the indexed codebase"
    )
    p_atlas_detect_patterns.add_argument("--project-root", default=os.getcwd())
    p_atlas_detect_patterns.add_argument("--json", action="store_true")
    p_atlas_detect_patterns.set_defaults(func=_cmd_atlas_detect_patterns)

    p_atlas_get_patterns = atlas_sub.add_parser(
        "get-patterns", help="List stored patterns in the Atlas database"
    )
    p_atlas_get_patterns.add_argument("--project-root", default=os.getcwd())
    p_atlas_get_patterns.add_argument("--json", action="store_true")
    p_atlas_get_patterns.set_defaults(func=_cmd_atlas_get_patterns)

    p_atlas_fn_impact = atlas_sub.add_parser(
        "function-impact", help="Analyze impact of a function by qualified name"
    )
    p_atlas_fn_impact.add_argument("qualified_name")
    p_atlas_fn_impact.add_argument("--project-root", default=os.getcwd())
    p_atlas_fn_impact.add_argument("--json", action="store_true")
    p_atlas_fn_impact.set_defaults(func=_cmd_atlas_analyze_function_impact)

    p_atlas_file_impact = atlas_sub.add_parser(
        "file-impact", help="Analyze impact of a file by path"
    )
    p_atlas_file_impact.add_argument("file_path")
    p_atlas_file_impact.add_argument("--project-root", default=os.getcwd())
    p_atlas_file_impact.add_argument("--json", action="store_true")
    p_atlas_file_impact.set_defaults(func=_cmd_atlas_analyze_file_impact)

    p_atlas_deps = atlas_sub.add_parser("dependencies", help="List dependencies of a file")
    p_atlas_deps.add_argument("file_path")
    p_atlas_deps.add_argument("--project-root", default=os.getcwd())
    p_atlas_deps.add_argument("--json", action="store_true")
    p_atlas_deps.set_defaults(func=_cmd_atlas_get_dependencies)

    p_atlas_dependents = atlas_sub.add_parser(
        "dependents", help="List dependents of a file"
    )
    p_atlas_dependents.add_argument("file_path")
    p_atlas_dependents.add_argument("--project-root", default=os.getcwd())
    p_atlas_dependents.add_argument("--json", action="store_true")
    p_atlas_dependents.set_defaults(func=_cmd_atlas_get_dependents)

    p_atlas_dupes = atlas_sub.add_parser("duplicates", help="Find duplicate artifacts")
    p_atlas_dupes.add_argument("--project-root", default=os.getcwd())
    p_atlas_dupes.add_argument("--json", action="store_true")
    p_atlas_dupes.set_defaults(func=_cmd_atlas_find_duplicates)

    p_atlas_cycles = atlas_sub.add_parser("cycles", help="Detect cycles")
    p_atlas_cycles.add_argument("--project-root", default=os.getcwd())
    p_atlas_cycles.add_argument("--json", action="store_true")
    p_atlas_cycles.set_defaults(func=_cmd_atlas_detect_cycles)

    p_atlas_glob = atlas_sub.add_parser(
        "glob", help="List Python files matching a glob pattern"
    )
    p_atlas_glob.add_argument("pattern")
    p_atlas_glob.add_argument("--project-root", default=os.getcwd())
    p_atlas_glob.add_argument("--limit", type=int, default=10)
    p_atlas_glob.add_argument("--json", action="store_true")
    p_atlas_glob.set_defaults(func=_cmd_atlas_glob)

    p_atlas_grep = atlas_sub.add_parser(
        "grep", help="Grep for text and return matching spans"
    )
    p_atlas_grep.add_argument("query")
    p_atlas_grep.add_argument("--project-root", default=os.getcwd())
    p_atlas_grep.add_argument("--limit", type=int, default=10)
    p_atlas_grep.add_argument("--path-glob", default=None)
    p_atlas_grep.add_argument("--json", action="store_true")
    p_atlas_grep.set_defaults(func=_cmd_atlas_grep_spans)

    p_atlas_search_spans = atlas_sub.add_parser(
        "search-spans", help="Span-first search for relevant code spans"
    )
    p_atlas_search_spans.add_argument("query")
    p_atlas_search_spans.add_argument("--project-root", default=os.getcwd())
    p_atlas_search_spans.add_argument("--limit", type=int, default=10)
    p_atlas_search_spans.add_argument("--json", action="store_true")
    p_atlas_search_spans.set_defaults(func=_cmd_atlas_search_spans)

    p_atlas_read_span = atlas_sub.add_parser(
        "read-span", help="Read a span of lines from a file"
    )
    p_atlas_read_span.add_argument("file_path")
    p_atlas_read_span.add_argument("start_line", type=int)
    p_atlas_read_span.add_argument("end_line", type=int)
    p_atlas_read_span.add_argument("--max-bytes", type=int, default=8192)
    p_atlas_read_span.add_argument("--project-root", default=os.getcwd())
    p_atlas_read_span.add_argument("--json", action="store_true")
    p_atlas_read_span.set_defaults(func=_cmd_atlas_read_span)

    p_atlas_fastapi_scaling_policy = atlas_sub.add_parser(
        "fastapi-scaling-policy",
        help="Inspect effective FastAPI scaling policy (.ranex/fastapi_scaling.yaml or defaults)",
    )
    p_atlas_fastapi_scaling_policy.add_argument("--project-root", default=os.getcwd())
    p_atlas_fastapi_scaling_policy.add_argument("--json", action="store_true")
    p_atlas_fastapi_scaling_policy.set_defaults(func=_cmd_atlas_fastapi_scaling_policy)

    p_atlas_fastapi_scaling_report = atlas_sub.add_parser(
        "fastapi-scaling-report",
        help="Run FastAPI scaling analysis",
    )
    p_atlas_fastapi_scaling_report.add_argument("--project-root", default=os.getcwd())
    p_atlas_fastapi_scaling_report.add_argument("--json", action="store_true")
    p_atlas_fastapi_scaling_report.set_defaults(func=_cmd_atlas_fastapi_scaling_report)

    p_atlas_fastapi_router_topology = atlas_sub.add_parser(
        "fastapi-router-topology",
        help="Analyze FastAPI router topology",
    )
    p_atlas_fastapi_router_topology.add_argument("--project-root", default=os.getcwd())
    p_atlas_fastapi_router_topology.add_argument("--json", action="store_true")
    p_atlas_fastapi_router_topology.set_defaults(func=_cmd_atlas_fastapi_router_topology)

    p_atlas_fastapi_truth_capsule = atlas_sub.add_parser(
        "fastapi-truth-capsule",
        help="Build a FastAPI truth capsule (static mode)",
    )
    p_atlas_fastapi_truth_capsule.add_argument("--project-root", default=os.getcwd())
    p_atlas_fastapi_truth_capsule.add_argument("--method", default=None)
    p_atlas_fastapi_truth_capsule.add_argument("--path", default=None)
    p_atlas_fastapi_truth_capsule.add_argument("--operation-id", default=None)
    p_atlas_fastapi_truth_capsule.add_argument("--handler-qualified-name", default=None)
    p_atlas_fastapi_truth_capsule.add_argument("--mode", default="static")
    p_atlas_fastapi_truth_capsule.add_argument("--strict", action="store_true")
    p_atlas_fastapi_truth_capsule.add_argument("--max-spans", type=int, default=1024)
    p_atlas_fastapi_truth_capsule.add_argument(
        "--max-dependency-depth", type=int, default=8
    )
    p_atlas_fastapi_truth_capsule.add_argument("--max-call-depth", type=int, default=6)
    p_atlas_fastapi_truth_capsule.add_argument("--max-call-nodes", type=int, default=256)
    p_atlas_fastapi_truth_capsule.add_argument(
        "--include-snippets", action="store_true"
    )
    p_atlas_fastapi_truth_capsule.add_argument(
        "--snippet-max-lines", type=int, default=0
    )
    p_atlas_fastapi_truth_capsule.add_argument("--json", action="store_true")
    p_atlas_fastapi_truth_capsule.set_defaults(func=_cmd_atlas_fastapi_truth_capsule)

    p_fw = sub.add_parser("firewall", help="Firewall policy operations")
    fw_sub = p_fw.add_subparsers(dest="firewall_command", required=True)

    p_fw_check = fw_sub.add_parser("check-import", help="Validate a single import")
    p_fw_check.add_argument("import_path")
    p_fw_check.add_argument("--project-root", default=os.getcwd())
    p_fw_check.add_argument("--json", action="store_true")
    p_fw_check.set_defaults(func=_cmd_firewall_check_import)

    p_fw_check_many = fw_sub.add_parser(
        "check-imports", help="Validate multiple imports"
    )
    p_fw_check_many.add_argument("import_paths", nargs="+")
    p_fw_check_many.add_argument("--project-root", default=os.getcwd())
    p_fw_check_many.add_argument("--json", action="store_true")
    p_fw_check_many.set_defaults(func=_cmd_firewall_check_imports)

    p_fw_analyze_file = fw_sub.add_parser(
        "analyze-file", help="Analyze a Python file for import violations"
    )
    p_fw_analyze_file.add_argument("file_path")
    p_fw_analyze_file.add_argument("--project-root", default=os.getcwd())
    p_fw_analyze_file.add_argument("--json", action="store_true")
    p_fw_analyze_file.set_defaults(func=_cmd_firewall_analyze_file)

    p_fw_typosquat = fw_sub.add_parser(
        "typosquat", help="Check if a package name looks like a typosquat"
    )
    p_fw_typosquat.add_argument("package_name")
    p_fw_typosquat.add_argument("--project-root", default=os.getcwd())
    p_fw_typosquat.add_argument("--json", action="store_true")
    p_fw_typosquat.set_defaults(func=_cmd_firewall_typosquat)

    p_fw_mode = fw_sub.add_parser("policy-mode", help="Print firewall policy mode")
    p_fw_mode.add_argument("--project-root", default=os.getcwd())
    p_fw_mode.set_defaults(func=_cmd_firewall_policy_mode)

    p_fw_blocked = fw_sub.add_parser(
        "blocked-patterns", help="List blocked patterns"
    )
    p_fw_blocked.add_argument("--project-root", default=os.getcwd())
    p_fw_blocked.add_argument("--json", action="store_true")
    p_fw_blocked.set_defaults(func=_cmd_firewall_blocked_patterns)

    p_fw_info = fw_sub.add_parser("info", help="Show firewall config source and summary")
    p_fw_info.add_argument("--project-root", default=os.getcwd())
    p_fw_info.add_argument("--json", action="store_true")
    p_fw_info.set_defaults(func=_cmd_firewall_policy_info)

    p_fw_rules = fw_sub.add_parser("list-rules", help="List firewall rules")
    p_fw_rules.add_argument("--project-root", default=os.getcwd())
    p_fw_rules.add_argument("--json", action="store_true")
    p_fw_rules.set_defaults(func=_cmd_firewall_list_rules)

    p_fw_allowed = fw_sub.add_parser(
        "allowed-packages", help="List allowed packages"
    )
    p_fw_allowed.add_argument("--project-root", default=os.getcwd())
    p_fw_allowed.add_argument("--json", action="store_true")
    p_fw_allowed.set_defaults(func=_cmd_firewall_allowed_packages)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
