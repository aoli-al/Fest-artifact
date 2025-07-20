## Fest Artifact Evaluation

## Introduction

This repository contains the artifact of the paper "Feedback-guided Adaptive Testing of Distributed Systems Designs". This README provides an overview of the artifact, how to run it, and the results.

We claim the following badges for the paper: 

- **Artifact Available**: Fest is available in this repository and part of the implementation has already been merged into the upstream P framework.
    - The `Fest` folder contains the implementation of Fest
        - `Src/PChecker/CheckerCore/SystematicTesting/Strategies/Feedback` contains the implementation of the feedback-guided schedule generation algorithm.
        - `Src/PChecker/CheckerCore/SystematicTesting/Strategies/Probabilistic` contains the extension of existing bounded-concurrency testing algorithms (POS, POS+)
        - `Src/PCompiler/CompilerCore/Parser/PParser.g4` contains the implementation of our scenario specification language
        - `Src/PCompiler/CompilerCore/Backend/CSharp/CSharpCodeGenerator.cs` converts scenarios to constraints
- **Functional**: The artifact is functional and can be used to run the benchmarks as described in the paper.

We do **not** claim the **Results Reproduced** badge as this artifact does not include proprietary distributed system models used in the evaluation.


## Getting Started Guide

### From Source

- You may clone this repository: `https://github.com/aoli-al/Fest-artifact`

- This project uses Nix to manage its dependencies. You may download [Nix](https://nixos.org/download.html) from here.

### From Docker

- You may also use the pre-configured container image that includes all the dependencies and tools to run the evaluation.

```
podman run -it leeleo3x/fest-artifact bash
```

## Build the Project

> [!NOTE]  
> If you are using the Docker image, you can skip this step as the image already contains the built project.

- Enter the project directory: `cd Fest-artifact`
- Enter the devshell: `nix develop`
- Build the project: `./Fest/Bld/build.sh`
- Next, you need to follow the instructions shown in the console to set the `pl` command: `alias pl='dotnet PATH_TO_FEST_ARTIFACT_FOLDER/Fest/Bld/Drops/Release/Binaries/net8.0/p.dll'`.

## Run the Evaluation

All open-source models are available in the `benchmarks` folder. The evaluation can be run on these models using the provided scripts.

## Kick the Tire (10 minutes)

- In this section, we show how to run the evaluation on the `Two Phase Commit` model.

- First, you need to enter the model folder: `cd benchmarks/2PC/2_TwoPhaseCommit`.
- Next, you need to build the model: `pl compile`.
- After the model is built, you can run the P checker to test the model.
    - First, you may run `pl check` to list all tests available for the model.
    - Then you can run `pl check --explore -tc <test_case> -t <timeout in seconds> --sch-<scheduler name> <other_experimental_flags>` to run the test case 
    - For example, you can run `pl check --explore -tc tcMultipleClientsNoFailureMoreData -t 60 --sch-feedbackpct 3`

Once you run the command, the P checker will start running the test case with the specified scheduler and timeout. The results will be printed to the console, including the elapsed time and the number of timelines generated. For example:

```
...
..... Schedule #100
Elapsed: 0.8052445, # timelines: 63
...
```

## Full (Functionality) Evaluation (~ 1 hour)

- Besides the arguments mentioned in the Kick the Tire section, you can also use the following arguments to run the evaluation:
    - Scheduler: 
        - `--sch-feedbackpct <value>`: This argument specifies the feedback-guided PCT algorithm with a specified concurrency level (3, 15, or 50).
        - `--sch-pct <value>`: This argument specifies the PCT algorithm with a specified concurrency level (3, 15, or 50).
        - `--sch-pos`: This argument specifies the POS algorithm. If you also specify the `--conflict-analysis` flag, it will run the POS+ algorithm.
        - `--sch-feedbackpos`: This argument specifies the feedback-guided POS algorithm. If you also specify the `--conflict-analysis` flag, it will run the feedback-guided POS+ algorithm.
        - `--sch-rl`: This argument specifies the Q-Learning algorithm.
    - Scenario:
        - `--pattern <Pattern>`: This argument specifies the scenario pattern to use.
    - Experimental flags:
        - `--no-priority-based`: This argument disables priority-based scheduling for feedback-based schedulers.
        - `--ignore-pattern`: Ignores the pattern feedback (only for feedback-based schedulers when a pattern is provided).


### Feedback-guided Schedule Generation 

You may use any of the feedback-guided schedulers mentioned above to test P models. For example, you can run the following command to test the `Two Phase Commit` model with the feedback-guided schedule generation algorithm at a concurrency level of 3:

```bash
pl check --explore -tc tcMultipleClientsNoFailureMoreData -t 60 --sch-feedbackpct 3
```

You may also compare it with the PCT algorithm at a concurrency level of 3:

```bash
pl check --explore -tc tcMultipleClientsNoFailureMoreData -t 60 --sch-pct 3
```

To understand the impact of priority-based schedule generation (RQ4), you can run the feedback-guided scheduler with the `--no-priority-based` flag to disable priority-based scheduling:

```bash
pl check --explore -tc tcMultipleClientsNoFailureMoreData -t 60 --sch-feedbackpct 3 --no-priority-based
```

### Scenario Specification Language

We provide a scenario specification example in the `benchmarks/2PC/2_TwoPhaseCommit/PSpec/Scenario.p` file. To test the model with scenario coverage, you can run the following command:

```bash
pl check --explore -tc tcMultipleClientsWithFailureMoreData -t 60 --pattern ConcurrentWriteThenRead
```

Note that this scenario checks whether the coordinator receives two write requests from different clients on the same key while a failure is injected between the two requests. So the scenario is only valid when there are multiple clients and a failure is injected. You can also run the same scenario with the feedback-guided scheduler:

```bash
pl check --explore -tc tcMultipleClientsWithFailureMoreData -t 60 --pattern ConcurrentWriteThenRead --sch-feedbackpct 3
```
You may also disable the scenario feedback by running the following command:

```bash
pl check --explore -tc tcMultipleClientsWithFailureMoreData -t 60 --pattern ConcurrentWriteThenRead --sch-feedbackpct 3 --ignore-pattern
```

## Optional: Run the Evaluation on All Open-Source Models

We provide a script to run the evaluation on all open-source models in the `benchmarks` folder. You can run the following command to execute the evaluation on all models:

```bash
python3 run_benchmark.py --cpus <number_of_concurrent_testing_processes> --time <timeout_in_seconds> --iter <number_of_repetitions>
```

For example, you can run the following command to execute the evaluation on all models with 4 concurrent testing processes, a timeout of 60 seconds, and no repetition:

```bash
python3 run_benchmark.py --cpus 4 --time 60 --iter 1
```

### Results

The results will be saved in the `bench_results` folder in the following format:

```
<TestName>-<Technique_Name>-origin-<Technique_Configuration>
└── <Repetition_Number>
    ├── BugFinding
    │   └── timeline.txt
    ├── stderr.txt
    └── stdout.txt
```

The `stdout.txt` file contains the output of the P checker, including the elapsed time and the number of timelines generated. 

