#!/usr/bin/env python3
import os
import subprocess
from multiprocessing import Pool
import argparse
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TECH = {
    "rl": ["origin"],
    "pct15": ["origin"],
    "feedbackpct15": ["origin", "origin-no-scen"],
    "pct3": ["origin"],
    "pct50": ["origin"],
    "pos": ["origin", "conflict-analysis"],
    "feedbackpct3": ["origin", "origin-no-scen"],
    "feedbackpct50": ["origin", "origin-no-scen"],
    "feedbackpos": ["origin", "conflict-analysis", "origin-no-scen", "ca-no-scen"],
}

HOME = os.path.expanduser('~')
P_BASE = f"{SCRIPT_DIR}/Fest/Bld/Drops/Release/Binaries/net8.0/p.dll"


def populate_configs():
    return {
        "origin": [],
        "conflict-analysis": ["--conflict-analysis"],
        "origin-no-scen": ["--ignore-pattern"],
        "ca-no-scen": ["--conflict-analysis", "--ignore-pattern"]
    }

def create_configs(out_dir, num_of_iter, time, bm_path):
    out_dir = os.path.abspath(out_dir)
    with open(os.path.join(SCRIPT_DIR, bm_path)) as f:
        compiled_benchmarks = set()
        for line in f:
            if not line.strip():
                continue
            [path, bench_name, *args] = [x.strip() for x in line.split(" ")]
            if path not in compiled_benchmarks:
                shutil.rmtree(os.path.join(path, "PForeign", "EventSeqMatcher.cs"), ignore_errors=True)
                shutil.rmtree(os.path.join(path, "PGenerated"), ignore_errors=True)
                subprocess.check_call(["dotnet", P_BASE, "compile"], cwd=path)
                compiled_benchmarks.add(path)
            for tech, config_names in TECH.items():
                for config_name in config_names:
                    if "scen" not in bm_path and "scen" in config_name:
                        continue
                    config = populate_configs()[config_name]
                    test_name = f"{bench_name}-{tech}-{config_name}"
                    for rep in range(num_of_iter):
                        work_dir = os.path.join(out_dir, test_name, str(rep))

                        out_path = os.path.join(work_dir, "stdout.txt")
                        if os.path.exists(out_path):
                            with open(out_path) as f:
                                txt = f.read()
                                #  if "... Elapsed " + str(time) in txt:
                                    #  continue
                        shutil.rmtree(work_dir, ignore_errors=True)
                        if "pct" in tech:
                            offset = 3
                            value = tech[tech.find("pct") + offset:]
                            tech_name = tech[: tech.find("pct") + offset]
                        else:
                            tech_name = tech
                        command = ["dotnet", P_BASE, "check", "--discard-after", "100", "--explore", "-o", work_dir, f"--sch-{tech_name}"]
                        if "pct" in tech_name:
                            command.append(value)
                        command.extend(args)
                        command.extend(config)
                        command.extend(["-t", str(time)])
                        os.makedirs(work_dir, exist_ok=True)
                        yield {
                            "command": command,
                            "stdout": os.path.join(work_dir, "stdout.txt"),
                            "stderr": os.path.join(work_dir, "stderr.txt"),
                            "cwd": path
                        }

def run_test(args):
    stdout = open(args["stdout"], "w")
    stderr = open(args["stderr"], "w")
    print(f"start:  {' '.join(args['command'])}")
    subprocess.call(args["command"], stdout=stdout, stderr=stderr, cwd=args["cwd"])
    print(f"done:  {' '.join(args['command'])}")

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("--out_dir", default="bench_results")
    parser.add_argument("--time", default=3 * 60 * 60, type=int)
    parser.add_argument("--iter", default=5, type=int)
    parser.add_argument("--cpus", default=80, type=int)
    parser.add_argument("--bm_path", default="valid_bms.txt")
    args = parser.parse_args()
    with Pool(processes=args.cpus) as pool:
        pool.map(run_test, create_configs(args.out_dir, args.iter, args.time, args.bm_path))
if __name__ == '__main__':
    main()
