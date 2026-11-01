# LibreLogin Minerest

Fork mínimo do [LibreLogin 0.24.0](https://github.com/kyngs/LibreLogin/tree/5cae5bd01fa37e45ee1d529bfa5c8eb1dcdc5c58), com o histórico original e a licença MPL-2.0 preservados.

A versão `0.24.0-minerest.2` troca apenas `Title.Times.of` por `Title.Times.times` para compatibilidade com o Adventure 5 do Velocity 4.3.0. Não altera as regras de autenticação.

[Diff da correção](https://github.com/luizroddev/librelogin-minerest/commit/b555f7d).

O uso em produção depende de aprovação do Luiz.

O build tenta também o repositório de releases do Libby (https://repo.alessiodp.com/releases/) no pluginManagement. O artefato antigo libby-gradle-plugin:plugin:1.2.1 não está disponível nele (HTTP 404).
