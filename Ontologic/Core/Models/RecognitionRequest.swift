// MARK: - RecognitionRequest.swift
// Encapsulates data sent to the recognition service.

import Foundation
import UIKit

/// The drawing data submitted to the recognition API.
struct RecognitionRequest: Codable {
    /// Base64-encoded PNG of the drawn strokes on a normalised canvas
    let imageData: String
    /// Canvas size used when drawing (for normalisation on server)
    let canvasWidth: Double
    let canvasHeight: Double
    /// Stroke count (can help the model prioritise candidates)
    let strokeCount: Int
    /// ISO 8601 timestamp
    let timestamp: String
    /// Client-side request identifier for deduplication / telemetry
    let requestID: UUID

    init(
        imageData: String,
        canvasWidth: Double,
        canvasHeight: Double,
        strokeCount: Int,
        timestamp: String = ISO8601DateFormatter().string(from: Date()),
        requestID: UUID = UUID()
    ) {
        self.imageData = imageData
        self.canvasWidth = canvasWidth
        self.canvasHeight = canvasHeight
        self.strokeCount = strokeCount
        self.timestamp = timestamp
        self.requestID = requestID
    }
}

// MARK: - Convenience init from UIImage

extension RecognitionRequest {
    /// Creates a request from a UIImage captured from the canvas.
    init?(
        image: UIImage,
        canvasSize: CGSize,
        strokeCount: Int
    ) {
        guard
            let pngData = image.pngData()
        else { return nil }

        self.init(
            imageData: pngData.base64EncodedString(),
            canvasWidth: Double(canvasSize.width),
            canvasHeight: Double(canvasSize.height),
            strokeCount: strokeCount
        )
    }
}
