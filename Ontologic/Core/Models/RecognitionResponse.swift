// MARK: - RecognitionResponse.swift
// Encapsulates data returned by the recognition service.

import Foundation

/// The response envelope returned by the recognition API.
struct RecognitionResponse: Codable {
    /// Mirrors the request ID for deduplication
    let requestID: UUID
    /// Ordered list of candidates, highest confidence first
    let candidates: [SymbolCandidate]
    /// Processing duration on the server (ms), for analytics
    let processingTimeMs: Double?
    /// API model / version that produced the result
    let modelVersion: String?

    /// True when at least one candidate was returned
    var hasResults: Bool { !candidates.isEmpty }

    /// Best candidate, or nil if empty
    var topCandidate: SymbolCandidate? { candidates.first }
}

// MARK: - RecognitionError

/// Typed errors that can arise during a recognition request.
enum RecognitionError: Error, LocalizedError {
    case networkUnavailable
    case serverError(statusCode: Int)
    case decodingFailed
    case imageEncodingFailed
    case rateLimited
    case unknown(underlying: Error)

    var errorDescription: String? {
        switch self {
        case .networkUnavailable:
            return "No internet connection. Please check your network."
        case .serverError(let code):
            return "Server error (HTTP \(code)). Please try again later."
        case .decodingFailed:
            return "Could not decode the server response."
        case .imageEncodingFailed:
            return "Could not process your drawing. Please try again."
        case .rateLimited:
            return "Too many requests. Please wait a moment and try again."
        case .unknown(let error):
            return "An unexpected error occurred: \(error.localizedDescription)"
        }
    }
}

// MARK: - Mock Data

extension RecognitionResponse {
    static let mockResponse = RecognitionResponse(
        requestID: UUID(),
        candidates: SymbolCandidate.mockCandidates,
        processingTimeMs: 312.5,
        modelVersion: "ontologic-mock-v1"
    )

    static let mockEmptyResponse = RecognitionResponse(
        requestID: UUID(),
        candidates: [],
        processingTimeMs: 88.0,
        modelVersion: "ontologic-mock-v1"
    )
}
