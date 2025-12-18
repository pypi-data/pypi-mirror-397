#!/bin/bash
# Patch RocketSim to fix constexpr issues with C++20 compilation
# This removes the constexpr specifier from the const operator[] which uses
# reinterpret_cast - not allowed in constant expressions

set -e

MATHTYPE_FILE="RocketSim/src/Math/MathTypes/MathTypes.h"

if [ ! -f "$MATHTYPE_FILE" ]; then
    echo "Error: $MATHTYPE_FILE not found"
    exit 1
fi

echo "Patching $MATHTYPE_FILE to remove constexpr from operator[]..."

# Backup the original file
cp "$MATHTYPE_FILE" "$MATHTYPE_FILE.bak"

# Remove constexpr from line 107 (const operator[])
# Use sed to replace "constexpr float operator[]" with "float operator[]"
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS sed syntax
    sed -i '' 's/constexpr float operator\[\](uint32_t index) const {/float operator\[\](uint32_t index) const {/g' "$MATHTYPE_FILE"
else
    # Linux sed syntax
    sed -i 's/constexpr float operator\[\](uint32_t index) const {/float operator\[\](uint32_t index) const {/g' "$MATHTYPE_FILE"
fi

echo "Patch applied successfully!"
echo "Original file backed up to $MATHTYPE_FILE.bak"
