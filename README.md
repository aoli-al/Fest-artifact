> [!WARNING]  
> Part of our implementation has already been merged into the upstream P repository. 
> Searching the commit history of P could potentially reveal our identity.


- - `P` folder contains the implementation of Fest
    - `Src/PChecker/CheckerCore/SystematicTesting/Strategies/Feedback` contains the implementation of feedback guided schedule generation algorithm.
    - `Src/PChecker/CheckerCore/SystematicTesting/Strategies/Probabilistic` contains the extension of existing bounded-concurrency testing algorithms (POS, POS+)
    - `Src/PCompiler/CompilerCore/Parser/PParser.g4` contains the implementation of our scenario specifcation language
    - `Src/PCompiler/CompilerCore/Backend/CSharp/CSharpCodeGenerator.cs` converts scenarios to constraints
- `open` contains the open-source P models.
- To run Fest on the open source models, you can use the script 
    - `python3 run_benchmark.py` 
    - For each test case, the script run 11 different techniques for 3 hour with 5 repetitions.
        - PCT3, PCT15, PCT50
        - Fest PCT3, Fest PCT15, Fest PCT50
        - POS, POS+
        - Fest POS, Fest POS+
        - Q-Learning
    - You can also configure the script with different parameters:      
        - `python3 run_benchmark.py --help`
