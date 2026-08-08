# Correct featuring-token selection in ftintitle

Review and correct the proposed featuring-token change already present in the working tree. The first split pass must recognize only explicit featuring markers such as `ft`, `feat`, and `featuring`; generic artist separators such as `&` belong only to the later artist fallback.

Make the correction in code, preserve custom featuring words, and keep title handling from splitting on generic artist separators.

Implement the task completely and correctly. Search and inspect the repository as needed, including related definitions and call sites. Choose the smallest coherent repair, run relevant existing tests and checks when practical, and preserve earlier task work in the persistent checkout.

Do not modify tests, generated files, dependency locks, or evaluation controls. Do not use network-dependent commands.
