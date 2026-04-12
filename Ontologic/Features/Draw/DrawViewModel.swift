// MARK: - DrawViewModel.swift

import SwiftUI
import Combine

// MARK: - State machine

enum DrawState {
    case idle
    case recognizing
    case success(RecognitionResponse)
    case failure(RecognitionError)
}

final class DrawViewModel: ObservableObject {

    // MARK: Published drawing state
    @Published var strokes: [Stroke] = []
    @Published var activeStroke: Stroke? = nil
    @Published var drawState: DrawState = .idle

    var canUndo: Bool { !strokes.isEmpty }
    var canRecognize: Bool { !strokes.isEmpty }
    var isRecognizing: Bool {
        if case .recognizing = drawState { return true }
        return false
    }

    // MARK: Canvas size — set by the view on appear
    var canvasSize: CGSize = .zero

    // MARK: Dependencies
    private let service: any RecognitionServiceProtocol

    init(service: any RecognitionServiceProtocol) {
        self.service = service
    }

    // MARK: Intents

    func undo() {
        guard !strokes.isEmpty else { return }
        strokes.removeLast()
    }

    func clear() {
        strokes = []
        activeStroke = nil
        drawState = .idle
    }

    @MainActor
    func recognize() async {
        guard canRecognize else { return }
        drawState = .recognizing

        // Build a snapshot image from current strokes
        let image = CanvasView.snapshot(strokes: strokes, size: canvasSize)

        guard let request = RecognitionRequest(
            image: image,
            canvasSize: canvasSize,
            strokeCount: strokes.count
        ) else {
            drawState = .failure(.imageEncodingFailed)
            return
        }

        do {
            let response = try await service.recognize(request)
            drawState = .success(response)
        } catch let error as RecognitionError {
            drawState = .failure(error)
        } catch {
            drawState = .failure(.unknown(underlying: error))
        }
    }

    func resetState() {
        drawState = .idle
    }
}
