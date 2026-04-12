// MARK: - RecognitionServiceProtocol.swift
// Protocol that every recognition service implementation must satisfy.
// Decouples the feature layer from concrete network or mock implementations.

import Foundation

/// Defines the contract for a symbol recognition service.
/// Implementations include MockRecognitionService (local) and
/// APIRecognitionService (live API).
protocol RecognitionServiceProtocol {
    /// Submits a recognition request and returns the response asynchronously.
    /// - Parameter request: The encoded drawing to be recognised.
    /// - Throws: `RecognitionError` on failure.
    func recognize(_ request: RecognitionRequest) async throws -> RecognitionResponse

    /// Fetches full symbol detail for a given candidate.
    /// - Parameter candidate: The candidate whose details are needed.
    /// - Throws: `RecognitionError` on failure.
    func fetchDetail(for candidate: SymbolCandidate) async throws -> SymbolDetail
}
