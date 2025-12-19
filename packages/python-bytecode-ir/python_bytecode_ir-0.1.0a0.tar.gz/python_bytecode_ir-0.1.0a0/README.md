# `python-bytecode-ir`

An expressive set of Python classes modeling Python bytecode as an SSA-form IR. Useful for static analysis and program
transformation. Upstream and downstream infrastructure still work in progress.

Base Classes

- IRInstruction
- IRValue

Code Stucture

- IRRegion(IRValue)
- IRBasicBlock(IRValue)

Atoms

- IRConstant(IRInstruction, IRValue)

Named Variable Access

- IRLoad(IRInstruction, IRValue)
- IRStore(IRInstruction)
- IRDelete(IRInstruction)

Special Loads

- IRImport(IRInstruction, IRValue)
- IRImportFrom(IRInstruction, IRValue)
- IRImportStar(IRInstruction)
- IRLoadBuiltIn(IRInstruction, IRValue)
- IRLoadRegion(IRInstruction, IRValue)

Unary Expressions

- IRUnaryOp(IRInstruction, IRValue)

Binary/In-place Expressions

- IRBinaryOp(IRInstruction, IRValue)
- IRInPlaceBinaryOp(IRInstruction)

Collection Literals

- IRBuildList(IRInstruction, IRValue)
- IRBuildTuple(IRInstruction, IRValue)
- IRBuildSet(IRInstruction, IRValue)
- IRBuildMap(IRInstruction, IRValue)

Subscriptions

- IRBuildSlice
- IRLoadSubscr
- IRStoreSubscr
- IRDeleteSubscr

Attribute Accesses

- IRLoadAttr(IRInstruction, IRValue)
- IRLoadSuperAttr(IRInstruction, IRValue)
- IRStoreAttr(IRInstruction)
- IRDeleteAttr(IRInstruction)

Unpacking

- IRUnpackSequence(IRInstruction, IRValue)
- IRUnpackEx(IRInstruction, IRValue)

F-string Related

- IRFormatString(IRInstruction, IRValue)
- IRConcatenateStrings(IRInstruction, IRValue)

Function Definitions and Calls

- IRMakeFunction(IRInstruction, IRValue)
- IRCall(IRInstruction, IRValue)
- IRCallFunctionEx(IRInstruction, IRValue)

Iterators

- IRGetIter(IRInstruction, IRValue)

Basic Block Terminators

- IRForIter(IRInstruction, IRValue)
- IRYield(IRInstruction, IRValue)
- IRBranch(IRInstruction)
- IRJump(IRInstruction)
- IRReturn(IRInstruction)
- IRRaise(IRInstruction)

Exception Stack Manipulation

- IRGetException(IRInstruction, IRValue)
- IRSetException(IRInstruction)

Other

- IRSetupAnnotations(IRInstruction)

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).