"""Target resolution - resolve call targets to fully qualified names."""

# TODO: Implement target resolution
# - Extended categories: local_function, self_method, inherited_method,
#   class_instantiation, imported_call, builtin, attribute_call, unresolved
# - Use import alias map, class method table, base-class lookup
# - Lightweight type inference from self.x = Foo() and annotations
# - Resolve self.x.method() through attribute types
