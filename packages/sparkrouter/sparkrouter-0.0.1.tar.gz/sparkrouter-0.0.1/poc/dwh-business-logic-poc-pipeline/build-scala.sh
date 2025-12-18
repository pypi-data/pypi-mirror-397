#!/bin/bash
set -e

echo "Building Scala project (sbt assembly)..."
cd scala
sbt assembly
cd ..

# assembly takes care of copying jars
#JAR_PATH="jars/decryption-udfs_2.12-1.0.0.jar"
#DEST_DIR="jars"
#DEST_PATH="$DEST_DIR/decryption-udfs_2.12-1.0.0.jar"
#
#mkdir -p "$DEST_DIR"
#
#if [ -f "$JAR_PATH" ]; then
#    echo "Copying Scala JAR to $DEST_PATH"
#    cp "$JAR_PATH" "$DEST_PATH"
#else
#    echo "Warning: Scala JAR not found at $JAR_PATH"
#fi
