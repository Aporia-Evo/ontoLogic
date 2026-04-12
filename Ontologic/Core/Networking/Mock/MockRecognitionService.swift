// MARK: - MockRecognitionService.swift
// In-memory mock that satisfies RecognitionServiceProtocol.
// Used in Previews, unit tests, and during development
// before the live API is available.

import Foundation

/// Simulates network latency and returns deterministic mock data.
final class MockRecognitionService: RecognitionServiceProtocol {

    // MARK: Configuration

    /// Simulated latency in seconds (default mirrors a realistic API round-trip).
    var simulatedDelay: TimeInterval = 1.5

    /// When set, `recognize` throws this error instead of returning results.
    var simulatedError: RecognitionError? = nil

    /// When true, returns an empty candidates list.
    var simulatesEmptyResult: Bool = false

    // MARK: RecognitionServiceProtocol

    func recognize(_ request: RecognitionRequest) async throws -> RecognitionResponse {
        // Simulate network round-trip
        try await Task.sleep(for: .seconds(simulatedDelay))

        if let error = simulatedError {
            throw error
        }

        if simulatesEmptyResult {
            return RecognitionResponse.mockEmptyResponse
        }

        return RecognitionResponse(
            requestID: request.requestID,
            candidates: SymbolCandidate.mockCandidates,
            processingTimeMs: simulatedDelay * 1000,
            modelVersion: "ontologic-mock-v1"
        )
    }

    func fetchDetail(for candidate: SymbolCandidate) async throws -> SymbolDetail {
        try await Task.sleep(for: .seconds(simulatedDelay * 0.5))

        if let error = simulatedError {
            throw error
        }

        return SymbolDetail.mock(for: candidate)
    }
}

// MARK: - Shared instance for Previews

extension MockRecognitionService {
    /// A zero-latency instance suitable for SwiftUI previews.
    static let preview: MockRecognitionService = {
        let service = MockRecognitionService()
        service.simulatedDelay = 0
        return service
    }()

    /// An error-producing instance for error-state previews.
    static let errorPreview: MockRecognitionService = {
        let service = MockRecognitionService()
        service.simulatedDelay = 0.5
        service.simulatedError = .networkUnavailable
        return service
    }()
}
