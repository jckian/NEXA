# STEP1: GPT
```
generate a program analysis of [precedent] including the number of cores, total height, dimensions, program, and the architecture
```

# STEP2: save as [precedent]-PROGRAM.md @reference folder


# STEP3: Claude Code agent
```
1. generate html
❯ using 3d-arch-diagram-gen agent create a js application to create a 3d diagram of the program listed in [precedent]-PROGRAM.md on a site with the dimensions of 70m x 70m.

2. generate [precedent]-PROGRAM-DISTRIBUTION.txt
❯ based on the format of ProgramFormat.txt create a more detailed floor by floor program distribution from  [precedent]-PROGRAM.md creating a category for each individual program type

3.
❯ update [precedent]-program-diagram to utilize this new program list

4.
❯ modify the app so all programs are represented as boxes. 
add in input allowing users to switch different program .md   files and specify target width, length, floor count and typical floor height parameters
```

# STEP4: GPT
```
我已經有一個已區分機能的massing了 把mcp prompt改成依照那個機能量體生成 一樣著重在結構+帷幕以及幾何形狀
```