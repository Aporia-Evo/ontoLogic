// MARK: - APIClient.swift
// Live URLSession-based implementation of RecognitionServiceProtocol.
// Switch the app to this service by replacing MockRecognitionService
// with APIRecognitionService in the dependency injection root.

import Foundation

/// Base configuration for the Ontologic REST API.
enum APIConfig {
    static let baseURL = URL(string: "https://api.ontologic.app/v1")!
    static let timeoutInterval: TimeInterval = 30

    enum Path {
        static let recognize = "/recognize"
        static func symbolDetail(id: String) -> String { "/symbols/\(id)" }
    }
}

// MARK: - APIRecognitionService

/// Live implementation that calls the Ontologic backend.
final class APIRecognitionService: RecognitionServiceProtocol {

    private let session: URLSession
    private let decoder: JSONDecoder

    init(session: URLSession = .shared) {
        self.session = session
        let d = JSONDecoder()
        d.keyDecodingStrategy = .convertFromSnakeCase
        d.dateDecodingStrategy = .iso8601
        self.decoder = d
    }

    // MARK: RecognitionServiceProtocol

    func recognize(_ request: RecognitionRequest) async throws -> RecognitionResponse {
        let url = APIConfig.baseURL.appendingPathComponent(APIConfig.Path.recognize)
        var urlRequest = URLRequest(url: url, timeoutInterval: APIConfig.timeoutInterval)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let encoder = JSONEncoder()
        encoder.keyEncodingStrategy = .convertToSnakeCase
        urlRequest.httpBody = try encoder.encode(request)

        return try await performRequest(urlRequest)
    }

    func fetchDetail(for candidate: SymbolCandidate) async throws -> SymbolDetail {
        let path = APIConfig.Path.symbolDetail(id: candidate.id.uuidString)
        let url = APIConfig.baseURL.appendingPathComponent(path)
        let urlRequest = URLRequest(url: url, timeoutInterval: APIConfig.timeoutInterval)
        return try await performRequest(urlRequest)
    }

    // MARK: Private

    private func performRequest<T: Decodable>(_ request: URLRequest) async throws -> T {
        do {
            let (data, response) = try await session.data(for: request)

            guard let http = response as? HTTPURLResponse else {
                throw RecognitionError.decodingFailed
            }

            guard (200..<300).contains(http.statusCode) else {
                if http.statusCode == 429 {
                    throw RecognitionError.rateLimited
                }
                throw RecognitionError.serverError(statusCode: http.statusCode)
            }

            return try decoder.decode(T.self, from: data)

        } catch let error as RecognitionError {
            throw error
        } catch let urlError as URLError {
            if urlError.code == .notConnectedToInternet || urlError.code == .networkConnectionLost {
                throw RecognitionError.networkUnavailable
            }
            throw RecognitionError.unknown(underlying: urlError)
        } catch {
            throw RecognitionError.unknown(underlying: error)
        }
    }
}
