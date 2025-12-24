# Rudi Agent Kernel

This example of kernel allows to interact in natural language with a RUDI node.

The kernel itself is a wrapper of ipykernel and [pydantic-ai-kernel](https://github.com/mariusgarenaux/pydantic-ai-kernel).

It takes as input text, process it with pydantic_ai agent, and returns text.

It can be installed on its own and used in any jupyter front end :

```bash
pip install rudi-kernel
jupyter console --kernel rudi
```

If you want to create new kernel-agent with pydantic_ai, you can copy this example agent.
