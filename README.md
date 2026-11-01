# LibreLogin Minerest

Fork mínimo do [LibreLogin 0.24.0](https://github.com/kyngs/LibreLogin/tree/5cae5bd01fa37e45ee1d529bfa5c8eb1dcdc5c58), com o histórico original e a licença MPL-2.0 preservados.

A versão `0.24.0-minerest.2` troca apenas `Title.Times.of` por `Title.Times.times` para compatibilidade com o Adventure 5 do Velocity 4.3.0. Não altera as regras de autenticação.

[Diff da correção](https://github.com/luizroddev/librelogin-minerest/commit/b555f7d).

O uso em produção depende de aprovação do Luiz.

O build tenta também o repositório de releases do Libby (https://repo.alessiodp.com/releases/) no pluginManagement. O artefato antigo libby-gradle-plugin:plugin:1.2.1 não está disponível nele (HTTP 404).

## Build diferencial

Requisitos: JDK 25 (`JAVA_HOME`), Python 3 e curl. Execute `python build-differential.py`.
O script verifica SHA-256 do jar oficial e das dependências, compila somente `AuthenticAuthorizationProvider` com javac 25 (`--release 21`), reproduz as relocations do upstream e substitui essa classe e sua classe interna. Atualiza somente os metadados da versão e preserva as demais classes, recursos e a licença. A constante da anotação `@Plugin` do bootstrap também recebe a versão do fork.

Saída: `build/differential/LibreLogin-0.24.0-minerest.2.jar`. Não é um rebuild integral do upstream: o Gradle 8.8 não executa no JDK 25, o plugin de licença antigo falha no Gradle 9, e o plugin Libby 1.2.1 não é resolvido mesmo com o repositório adicional. O builder segue o procedimento diferencial já empregado no Minerest, sem trazer as mudanças de autenticação daquele outro fork.

O código-fonte completo correspondente está neste repositório e no ZIP de fontes da release. O comportamento alterado é exclusivamente a fábrica de temporização de título compatível com Adventure 5.
