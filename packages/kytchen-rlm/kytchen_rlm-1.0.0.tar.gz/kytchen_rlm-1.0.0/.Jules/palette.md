# Palette's Journal - Critical Learnings

This journal records critical UX and accessibility learnings specific to this application.

## 2024-05-22 - [Example Entry]
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2025-05-22 - Loading States in Radix UI
**Learning:** Radix UI `Slot` component (used for `asChild`) cannot handle multiple children. Injecting a loading spinner into a component that uses `asChild` requires careful handling or disabling `asChild`.
**Action:** When adding `isLoading` props to Radix-based components, conditionally render the loader only when `asChild` is false, or wrap the children if `asChild` is necessary (though wrapping breaks the `asChild` contract often).
