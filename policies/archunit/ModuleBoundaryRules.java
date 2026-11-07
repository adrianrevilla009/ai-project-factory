// Ejemplo de reglas ArchUnit para monolito modular: solo la API pública de un módulo es accesible.
// TODO-VERIFY: versión de archunit-junit5 y API slices() contra la documentación oficial.
package com.example.architecture;

import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchRule;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;
import static com.tngtech.archunit.library.dependencies.SlicesRuleDefinition.slices;

@AnalyzeClasses(packages = "com.example.app")
class ModuleBoundaryRules {

    @ArchTest
    static final ArchRule modules_are_free_of_cycles =
        slices().matching("com.example.app.(*)..").should().beFreeOfCycles();

    @ArchTest
    static final ArchRule internals_are_not_accessed_from_other_modules =
        noClasses().that().resideOutsideOfPackage("com.example.app.orders..")
            .should().dependOnClassesThat().resideInAPackage("com.example.app.orders.internal..");
}
