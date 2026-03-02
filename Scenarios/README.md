# Errors
This tool can handle many scenarios in which the following errors occur:
- E0451
- E0433
- E0451
- E0603


# Scenarios
## Correct
- Correct code. The tool does not report issues or fixes.

## Scope
- Scope1: Use of undeclared module in client.rs.

## Visibility
- Visibility1: library.rs function bar is private; but client.rs uses it directly.
- Visibility2: library.rs struct Vector is private; but client.rs uses it directly.
- Visibility3: library.rs field x of struct Vector is private; but client.rs uses it directly.
- Visibility4: library.rs field x and y of struct Vector are private; but client.rs uses them directly.
- Visibility5: library.rs defines many private fields in struct Vector; but client.rs uses them directly.
- Visibility6: client.rs defines internal mod but a client uses them directly.
- Visibility7: library.rs defines internal mod math; client.rs uses it directly.
- Visibility8: library.rs defines internal mod math with private symbols; but client.rs uses them directly.
- VisibilityCombined: Combination of all previous visibility issues.

## Combined
- Combined1: A scenario that combines almost every issue this tool can "fix".
