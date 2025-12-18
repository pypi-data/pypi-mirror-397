package com.shutterfly.dwh.udfs

import com.shutterfly.platform.infrastructure.util.SecurityUtils
import org.apache.spark.sql.api.java.{UDF1, UDF2, UDF3}
import org.apache.spark.sql.types._
import org.apache.spark.sql.catalyst.expressions.GenericRowWithSchema

/**
 * High-performance Scala UDFs for decryption operations.
 * 
 * These UDFs run directly on Spark executors, enabling parallel decryption
 * across the cluster. This is critical for high-throughput processing of
 * millions of records with unique encrypted values.
 * 
 * Usage from PySpark:
 * {{{
 * spark.udf.registerJavaFunction("decrypt_value", "com.shutterfly.dwh.udfs.DecryptionUDFs.decrypt", StringType())
 * df.withColumn("decrypted", expr("decrypt_value(encrypted_col)"))
 * }}}
 */
object DecryptionUDFs {

  /**
   * Primary decryption function.
   * Handles versioned encryption (v3, v4 prefixes) and fallback logic.
   *
   * @param encrypted The encrypted string value
   * @return Decrypted string, or null if decryption fails
   */
  def decrypt(encrypted: String): String = {
    if (encrypted == null || encrypted.trim.isEmpty) {
      return null
    }

    try {
      // First attempt: safeDecode
      val decoded = SecurityUtils.safeDecode(encrypted)
      
      if (decoded != null && decoded.trim.nonEmpty) {
        return decoded
      }
      
      // Fallback: handle versioned encryption
      val toDecrypt = if (encrypted.startsWith("v4") || encrypted.startsWith("v3")) {
        encrypted.substring(2)
      } else if (encrypted.length > 1) {
        encrypted.substring(1)
      } else {
        encrypted
      }
      
      val fallbackDecoded = SecurityUtils.decode2(toDecrypt)
      if (fallbackDecoded != null && fallbackDecoded.trim.nonEmpty) {
        fallbackDecoded
      } else {
        null
      }
    } catch {
      case _: Exception => null
    }
  }

  /**
   * Decode media path from decrypted imageId.
   * Returns a struct with (msp, mspid, mediaid, userid).
   *
   * @param decryptedImageId The decrypted image ID string
   * @return Row with media path components, or null
   */
  def decodeMediaPath(decryptedImageId: String): org.apache.spark.sql.Row = {
    if (decryptedImageId == null || decryptedImageId.trim.isEmpty) {
      return null
    }

    val IMAGE_PREFIX = "Image:"
    val pathTokens = decryptedImageId.split(":")

    if (pathTokens.isEmpty || pathTokens(0) != "MSP") {
      return null
    }

    try {
      // Case 1: MSP:Image:ID format
      if (pathTokens.length == 3 && pathTokens(1) == "Image") {
        val idStr = pathTokens(2)
        val idLong = try { idStr.toLong } catch { case _: NumberFormatException => 0L }

        // Check if ID > Integer.MAX_VALUE to determine mspid vs mediaid
        if (idLong > Int.MaxValue) {
          return createMediaPathRow(
            msp = IMAGE_PREFIX + idStr,
            mspid = null,
            mediaid = idStr,
            userid = null
          )
        } else {
          return createMediaPathRow(
            msp = IMAGE_PREFIX + idStr,
            mspid = idStr,
            mediaid = null,
            userid = null
          )
        }
      }

      // Case 2: MSP:USERID:Image:ID format
      if (pathTokens.length == 4 && pathTokens(2) == "Image") {
        val userid = pathTokens(1)
        val idStr = pathTokens(3)
        val idLong = try { idStr.toLong } catch { case _: NumberFormatException => 0L }

        // Check if ID > Integer.MAX_VALUE to determine mspid vs mediaid
        if (idLong > Int.MaxValue) {
          return createMediaPathRow(
            msp = IMAGE_PREFIX + idStr,
            mspid = null,
            mediaid = idStr,
            userid = userid
          )
        } else {
          return createMediaPathRow(
            msp = IMAGE_PREFIX + idStr,
            mspid = idStr,
            mediaid = null,
            userid = userid
          )
        }
      }

      // Case 3: Path format with /user/ in it
      if (pathTokens.length >= 2) {
        val path = pathTokens(1)
        if (path.contains("/user/")) {
          val pathParts = path.split("/")
          val userIdx = pathParts.indexOf("user")
          if (userIdx >= 0 && userIdx + 1 < pathParts.length) {
            val userid = pathParts(userIdx + 1)
            val mediaid = try {
              pathParts.last.toLong.toString
            } catch {
              case _: NumberFormatException => null
            }
            return createMediaPathRow(
              msp = decryptedImageId,
              mspid = null,
              mediaid = mediaid,
              userid = userid
            )
          }
        }
      }

      null
    } catch {
      case _: Exception => null
    }
  }

  /**
   * Parse location spec from decrypted data string.
   *
   * The decrypted data uses a custom encoding format where fields are marked by single characters:
   * - 'u' followed by 12 chars: userid
   * - 'b' followed by 8 hex chars: color balance
   * - 'd' followed by 8 hex chars: dimensions
   * - 'l' followed by 4 hex chars (length) then filename: locationspec
   * - etc.
   *
   * This logic is ported from com.shutterfly.dwh.decode.ImageDataDecoder.decodeMediaData()
   *
   * @param decryptedData The decrypted data string in custom encoded format
   * @return The location spec value (filename), or null
   */
  def parseLocationSpec(decryptedData: String): String = {
    if (decryptedData == null || decryptedData.trim.isEmpty) {
      return null
    }

    try {
      var i = 0
      while (i < decryptedData.length) {
        val marker = decryptedData.charAt(i)
        i += 1 // Move past marker

        marker match {
          case 'l' =>
            // Found location spec marker
            // Next 4 chars are hex-encoded length
            if (i + 4 > decryptedData.length) {
              return null
            }

            val lengthHex = decryptedData.substring(i, i + 4)
            i += 4

            val filenameLength = try {
              // dehex16: decode 4 hex chars to 16-bit int
              Integer.parseInt(lengthHex, 16)
            } catch {
              case _: NumberFormatException => return null
            }

            if (filenameLength <= 0 || filenameLength > 500) {
              return null // Sanity check
            }

            // Extract filename
            if (i + filenameLength > decryptedData.length) {
              return null
            }

            val filename = decryptedData.substring(i, i + filenameLength)
            return filename

          case 'u' =>
            // userid: 12 fixed chars
            i += 12

          case 'b' =>
            // color balance: 8 hex chars
            i += 8

          case 'd' =>
            // dimensions: 8 hex chars (4 for width, 4 for height)
            i += 8

          case 'h' =>
            // histogram: 4 hex chars
            i += 4

          case 'm' =>
            // last modified: 16 hex chars (64-bit)
            i += 16

          case 'o' =>
            // orientation: 1 hex char
            i += 1

          case 't' =>
            // TTL: 16 hex chars (64-bit)
            i += 16

          case 'v' =>
            // version: 1 char
            i += 1

          case 'r' =>
            // red-eye data: skip complex structure
            // First: param length (4 hex) + params
            if (i + 4 > decryptedData.length) return null
            val paramLen = Integer.parseInt(decryptedData.substring(i, i + 4), 16)
            i += 4 + paramLen

            // Then: rect count (4 hex) + rects (each is 16 hex chars)
            if (i + 4 > decryptedData.length) return null
            val rectCount = Integer.parseInt(decryptedData.substring(i, i + 4), 16)
            i += 4 + (rectCount * 16)

          case _ =>
            // Unknown marker - this shouldn't happen with valid data
            return null
        }
      }

      null // 'l' marker not found
    } catch {
      case _: Exception => null
    }
  }

  /**
   * Combined UDF: Decrypt and parse image data in one call.
   * Returns a struct with all extracted fields.
   *
   * This is the most efficient approach - single UDF call per row
   * that does decrypt + parse in one executor-side operation.
   *
   * @param imageView The image_view string (may contain encrypted values)
   * @param imageId The encrypted image ID (may be null if in imageView)
   * @param imageData The encrypted image data (may be null if in imageView)
   * @return Row with (msp, mspid, mediaid, locationspec)
   */
  def decryptAndParse(imageView: String, imageId: String, imageData: String): org.apache.spark.sql.Row = {
    try {
      var effectiveImageId = imageId
      var effectiveImageData = imageData

      // Parse imageView if present
      if (imageView != null && imageView.nonEmpty) {
        val viewData = parseImageView(imageView)
        
        if (effectiveImageId == null) {
          effectiveImageId = viewData.getOrElse("imageid", null)
        }
        if (effectiveImageData == null) {
          effectiveImageData = viewData.getOrElse("data", null)
        }

        // Case: Plain view data (no decryption needed)
        if (effectiveImageId == null && effectiveImageData == null) {
          val msp = viewData.getOrElse("msp", null)
          val slocspec = viewData.getOrElse("slocspec", null)
          var mediaid = viewData.getOrElse("mediaid", null)
          var mspid: String = null

          // Extract mediaid/mspid from msp if needed
          if (mediaid == null && msp != null && msp.startsWith("Image:")) {
            val idVal = msp.substring(6) // after "Image:"
            try {
              val idLong = idVal.toLong
              if (idLong > 0x7fffffffL) {
                mediaid = idVal
              } else {
                mspid = idVal
              }
            } catch {
              case _: NumberFormatException => // ignore
            }
          }

          if (msp != null || slocspec != null) {
            return createResultRow(msp, mspid, mediaid, slocspec)
          }
        }
      }

      // Decrypt if we have encrypted values
      if (effectiveImageId != null && effectiveImageData != null) {
        val decryptedId = decrypt(effectiveImageId)
        val decryptedData = decrypt(effectiveImageData)

        if (decryptedId != null && decryptedData != null) {
          val mediaPath = decodeMediaPath(decryptedId)
          val locationSpec = parseLocationSpec(decryptedData)

          if (mediaPath != null) {
            return createResultRow(
              mediaPath.getString(0), // msp
              mediaPath.getString(1), // mspid
              mediaPath.getString(2), // mediaid
              locationSpec
            )
          } else {
            return createResultRow(null, null, null, locationSpec)
          }
        }
      }

      createResultRow(null, null, null, null)
    } catch {
      case _: Exception => createResultRow(null, null, null, null)
    }
  }

  // Helper: Parse image_view string into key-value map
  private def parseImageView(imageView: String): Map[String, String] = {
    if (imageView == null) return Map.empty
    
    imageView.split("&").flatMap { part =>
      val eqIdx = part.indexOf('=')
      if (eqIdx > 0) {
        val key = part.substring(0, eqIdx).toLowerCase
        var value = part.substring(eqIdx + 1)
        // Handle [value] format
        if (value.startsWith("[") && value.endsWith("]")) {
          value = value.substring(1, value.length - 1)
        }
        // Take first value if comma-separated
        val firstValue = value.split(",").headOption.getOrElse(value)
        Some(key -> firstValue)
      } else {
        None
      }
    }.toMap
  }

  // Helper: Create result row for decryptAndParse
  private def createResultRow(msp: String, mspid: String, mediaid: String, locationspec: String): org.apache.spark.sql.Row = {
    org.apache.spark.sql.Row(msp, mspid, mediaid, locationspec)
  }

  // Helper: Create media path row
  private def createMediaPathRow(msp: String, mspid: String, mediaid: String, userid: String): org.apache.spark.sql.Row = {
    org.apache.spark.sql.Row(msp, mspid, mediaid, userid)
  }

  /**
   * Schema for the decryptAndParse return type.
   * Use this when registering the UDF.
   */
  val decryptAndParseSchema: StructType = StructType(Seq(
    StructField("msp", StringType, nullable = true),
    StructField("mspid", StringType, nullable = true),
    StructField("mediaid", StringType, nullable = true),
    StructField("locationspec", StringType, nullable = true)
  ))

  val mediaPathSchema: StructType = StructType(Seq(
    StructField("msp", StringType, nullable = true),
    StructField("mspid", StringType, nullable = true),
    StructField("mediaid", StringType, nullable = true),
    StructField("userid", StringType, nullable = true)
  ))
}


/**
 * Java-compatible UDF wrapper for simple decryption.
 * Register with: spark.udf.register("decrypt_value", new DecryptUDF(), StringType())
 */
class DecryptUDF extends UDF1[String, String] {
  override def call(encrypted: String): String = {
    DecryptionUDFs.decrypt(encrypted)
  }
}


/**
 * Java-compatible UDF wrapper for combined decrypt and parse.
 * This is the recommended UDF for the ImageTransformer use case.
 * 
 * Register with:
 * spark.udf.register("decrypt_and_parse", new DecryptAndParseUDF(), DecryptionUDFs.decryptAndParseSchema)
 */
class DecryptAndParseUDF extends UDF3[String, String, String, org.apache.spark.sql.Row] {
  override def call(imageView: String, imageId: String, imageData: String): org.apache.spark.sql.Row = {
    DecryptionUDFs.decryptAndParse(imageView, imageId, imageData)
  }
}
