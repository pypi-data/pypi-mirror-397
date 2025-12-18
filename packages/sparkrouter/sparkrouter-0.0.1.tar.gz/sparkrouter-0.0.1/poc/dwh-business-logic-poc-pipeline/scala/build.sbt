name := "decryption-udfs"
version := "1.0.0"
scalaVersion := "2.12.18"

// Spark 3.x uses Scala 2.12
libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-sql" % "3.3.0" % "provided"
)

// Reference to your existing platform.infrastructure JAR
// Path is relative to the scala/ directory (where build.sbt lives)
// Since scala/ is inside the project, go up one level to reach jars/
// unmanagedJars in Compile += file("../jars/platform.infrastructure-1.19.5-SNAPSHOT.jar")
unmanagedJars in Compile += file("platform_infrastructure/platform.infrastructure-1.19.5-SNAPSHOT.jar")

// Ensure we can resolve maven central
resolvers += "Maven Central" at "https://repo1.maven.org/maven2/"

// Assembly settings
assembly / assemblyJarName := "decryption-udfs_2.12-1.0.0.jar"

// Merge strategy for assembly
assembly / assemblyMergeStrategy := {
  case PathList("META-INF", xs @ _*) => MergeStrategy.discard
  case "reference.conf" => MergeStrategy.concat
  case _ => MergeStrategy.first
}

// Exclude Spark and Scala from assembly (they're provided at runtime)
assembly / assemblyExcludedJars := {
  val cp = (assembly / fullClasspath).value
  cp filter { jar =>
    jar.data.getName.contains("spark-") ||
    jar.data.getName.contains("scala-library") ||
    jar.data.getName.contains("hadoop-")
  }
}

// Output directory for the assembled JAR
assembly / assemblyOutputPath := file("../jars/decryption-udfs_2.12-1.0.0.jar")

// Task to copy the dependency JAR to ../jars
Compile / compile := {
  val _ = (Compile / compile).value
  IO.copyFile(
    file("platform_infrastructure/platform.infrastructure-1.19.5-SNAPSHOT.jar"),
    file("../jars/platform.infrastructure-1.19.5-SNAPSHOT.jar")
  )
  (Compile / compile).value
}