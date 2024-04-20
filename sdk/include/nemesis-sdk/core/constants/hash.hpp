#pragma once
#include "../types.hpp"

namespace Nemesis::Core
{
	constexpr u64 FNV1A64(const char* szInput, u64 uHash = 0xcbf29ce484222325)
	{
		constexpr u64 uPrime = 0x100000001b3;

		// @note / SapDragon: Iterate over the input string
		while (*szInput)
		{
			uHash ^= *szInput++;
			uHash *= uPrime;
		}
		return uHash;
	}

	constexpr u32 FNV1A32(const char* szInput, u32 uHash = 0x811c9dc5)
	{
		constexpr u32 uPrime = 0x1000193;

		// @note / SapDragon: Iterate over the input string
		while (*szInput)
		{
			uHash ^= *szInput++;
			uHash *= uPrime;
		}
		return uHash;
	}
}

#define FHASH_64(str) Nemesis::Core::FNV1A64(str)
#define FHASH_32(str) Nemesis::Core::FNV1A32(str)