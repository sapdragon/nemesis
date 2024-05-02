# Nemesis Packet Language

Nemesis packet language was created to describe the structure of binary data packets with minimal disclosure. It allows defining the hierarchy of packets, their fields, and data types. The language has a simple and intuitive syntax that facilitates the description of packets.
It is inspired by the Telegram and Protobuf data packet description languages.

Where Nemesis falls short compared to other data packet description languages:
- Convenience: Nemesis does not always use all the features of the language during code generation, due to the possibility of abusing them through reverse engineering.
- Immaturity: Nemesis is a Proof of Concept and does not have all the capabilities of other data packet description languages.

## Specification
The data packet specification consists of several sections:
- General Information
- Syntax
- Binary Packet Description
- Capabilities for Complicating Reverse Engineering

### General Information
- Specification files have the `.ns` extension.
- Data packet specification files must be in UTF-8 encoding.

### Syntax
A packet is defined using the `package` keyword, followed by the packet name and a block enclosed in curly braces `{}`:
```
package <name> {
    ...
}
```

Inside the packet block, fields can be defined. Each field has a name and a data type, separated by a colon `:`:

```
package <name> {
    <field_name>: <type>;
}
```

Data types can be primitive or composite. Primitive data types:

- `u8` - 8-bit unsigned integer
- `u16` - 16-bit unsigned integer
- `u32` - 32-bit unsigned integer
- `u64` - 64-bit unsigned integer
- `i8` - 8-bit signed integer
- `i16` - 16-bit signed integer
- `i32` - 32-bit signed integer
- `i64` - 64-bit signed integer
- `f32` - 32-bit floating-point number
- `f64` - 64-bit floating-point number
- `bool` - Boolean value
- `string` - string (actually a structure that contains the string length and a u8 slice)

Composite data types:
- `[]<type>` - a slice (a variable-length array) of elements of type `<type>`
- `[<size>]<type>` - a fixed-length array of `<size>` elements of type `<type>`


Nemesis supports constant generics, which are determined at compile-time. Generics allow the creation of parameterized packets, where the data types of the fields can be specified when using the packet.
To define a generic, angle brackets `< >` are used after the packet name, inside which the names of the type parameters are specified:
```
package name<T1, T2> {
    field1: T1;
    field2: T2;
}
```

When using a parameterized packet, it is necessary to specify the concrete data types for the type parameters:
```
package some_package {
    field1: name<u8, u16>;
}
```

In this example `field1` is a concrete instantiation of the `name` packet, where `T1` is replaced with `u8`, and `T2` with `u16`.

Generics in Nemesis are constant and are determined at compile-time. This means that all type parameters must be known at the compilation stage and cannot be changed during runtime (which is logical, since Nemesis is a language for describing data packets, not a programming language).

Packets can inherit from other packets using `:`:

```
package <name> : <parent> {
    ...
}
```

The language supports C++-style comments:

```
// Single-line comment

/* Multi-line
comment */
```

### Binary Packet Description

A binary packet consists of the following parts:

- Header: 4 bytes. The checksum of the packet name, calculated using the CRC32 algorithm. Used for packet identification.

- Packet content: Binary representation of the packet fields according to their data types and declaration order.

Packet fields follow each other in the order in which they are declared in the packet description. Nested packets are also included in the content of the parent packet.

### Capabilities for Complicating Reverse Engineering

To complicate reverse engineering, the code generator does not generate unnecessary information about the packet. Instead, it generates a minimal set of methods for reading and writing the packet, as well as methods for accessing packet fields.

For added protection, you can add obfuscation or virtualization to the packet field access methods.