## Fest Artifact Evaluation

## Introduction

This repository contains artifact of the paper "Feedback-guided Adaptive Testing of Distributed Systems Designs". This README provides an overview of the artifact, how to run it, and the results.

We claim the following badge for the paper: 

- **Artifact Available**: Fest is available in this repository and part of the implementation is already merged into the upstream P framework.
    - `Fest` folder contains the implementation of Fest
        - `Src/PChecker/CheckerCore/SystematicTesting/Strategies/Feedback` contains the implementation of feedback guided schedule generation algorithm.
        - `Src/PChecker/CheckerCore/SystematicTesting/Strategies/Probabilistic` contains the extension of existing bounded-concurrency testing algorithms (POS, POS+)
        - `Src/PCompiler/CompilerCore/Parser/PParser.g4` contains the implementation of our scenario specifcation language
        - `Src/PCompiler/CompilerCore/Backend/CSharp/CSharpCodeGenerator.cs` converts scenarios to constraints
- **Functional**: The artifact is functional and can be used to run the benchmarks as described in the paper.

We do **not** claim the **Results Reproduced** badge as this artifact does not include proprietary distributed system models used in the evaluation.


## Getting Started Guide

### From Source

- You may clone this repository: `https://github.com/aoli-al/Fest-artifact`

- The project uses Nix to manage its dependencies. You may download [Nix](https://nixos.org/download.html) from here.

### From Docker

- You may also use the pre-configured container image that includes all the dependencies and tools to run the evaluation.


## Build the Project

> [!NOTE]  
> If youa are using the Docker image, you can skip this step as the image already contains the built project.

- Enter the project directory: `cd Fest-artifact`
- Enter the devshell: `nix develop`
- Build the project: `./Fest/Bld/build.sh`
- Next you need to follow the instruction showing in the console to set the `pl` command: `alias pl='dotnet PATH_TO_FEST_AETIFACT_FOLDER/Fest/Bld/Drops/Release/Binaries/net8.0/p.dll`.

## Run the Evaluation

All open-source models are available in the `benchmarks` folder. The evaluation can be run on these models using the provided scripts.

## Kick the Tire (10 minutes)

- In this section, we show how to run the evaluation on the `Two Phase Commit` model.

- First, you need to enter the model folder: `cd benchmarks/2PC/2_TwoPhaseCommit`.
- Next you need to build the model: `pl compile`.
- After the model is built, you can run the P checker to test the model.
    - First you run may run `pl check` to list all tests avaiable for the model.
    - Then you can run `pl check --explore -tc <test_case> -t <timeout in seconds> --sch-<scheduler name> <other_experimental_flags>` to run the test case 
    - For example, you can run `pl check --explore -tc tcMultipleClientsNoFailureMoreData -t 60 --sch-feedbackpct 3`

Once you run the command, the P checker will start running the test case with the specified scheduler and timeout. The results will be printed to the console, including the elapsed time and the number of timelines generated. For example:

```
...
..... Schedule #100
Elapsed: 0.8052445, # timelines: 63
...
```

## Full Evaluation (~ 1 hour)

- Besides the arguments mentioned in the Kick the Tire section, you can also use the following arguments to run the evaluation:
    - Scheduler: 
        - `--sch-feedbackpct <value>`: This argument specifies the feedback-guided schedule generation algorithm with a specified concurrency level (3, 15, or 50).
        - `--sch-pct <value>`: This argument specifies the PCT algorithm with a specified concurrency level (3, 15, or 50).
        - `--sch-pos`: This argument specifies the POS algorithm.
        - `--sch-feedbackpos`: This argument specifies the POS+ algorithm.
        - `--sch-rl`: This argument specifies the Q-Learning algorithm.
    - Scenario:
        - `--pattern <Pattern>`: This argument specifies the scenario pattern to use.
    - Experimental flags:
        - `--no-priority-based`: This argument disables the priority-based scheduling for feedback-based schedulers.
        - `--ignore-pattern`: Ignore the pattern feedback (only for feedback-based schedulers when pattern is provided).



