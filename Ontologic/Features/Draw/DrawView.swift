// MARK: - DrawView.swift
// Main drawing screen. Houses the canvas and its control toolbar.

import SwiftUI

struct DrawView: View {

    @StateObject var viewModel: DrawViewModel

    /// Called when recognition completes successfully (e.g. to persist history).
    var onResultsReady: ((RecognitionResponse) -> Void)?

    // Navigation to results
    @State private var navigateToResults: RecognitionResponse? = nil

    var body: some View {
        ZStack {
            Color.ontoBackground_fallback().ignoresSafeArea()

            VStack(spacing: 0) {
                instructionBanner

                // Canvas
                GeometryReader { geo in
                    CanvasView(
                        strokes: $viewModel.strokes,
                        activeStroke: $viewModel.activeStroke
                    )
                    .cornerRadius(20)
                    .padding(16)
                    .onAppear {
                        viewModel.canvasSize = geo.size
                    }
                    .onChange(of: geo.size) { newSize in
                        viewModel.canvasSize = newSize
                    }
                }

                controlBar
            }

            // Recognizing overlay
            if viewModel.isRecognizing {
                Color.black.opacity(0.4).ignoresSafeArea()
                LoadingView(message: "Recognising symbol…")
                    .ontoCard()
                    .padding(32)
            }
        }
        .navigationTitle("Draw Symbol")
        .navigationBarTitleDisplayMode(.inline)
        .navigationDestination(item: $navigateToResults) { response in
            ResultsView(viewModel: ResultsViewModel(response: response))
        }
        .alert(
            "Recognition Failed",
            isPresented: alertIsPresented,
            presenting: alertError
        ) { _ in
            Button("OK") { viewModel.resetState() }
        } message: { error in
            Text(error.localizedDescription)
        }
        .onChange(of: drawStateVersion) { _ in
            if case .success(let response) = viewModel.drawState {
                onResultsReady?(response)
                navigateToResults = response
            }
        }
    }

    // MARK: Subviews

    private var instructionBanner: some View {
        Text("Draw a symbol in the canvas below")
            .font(.ontoBodyMedium)
            .foregroundColor(.ontoTextSecondary_fallback())
            .padding(.top, 12)
    }

    private var controlBar: some View {
        HStack(spacing: 16) {
            OIconButton(
                "arrow.uturn.backward",
                accessibilityLabel: "Undo last stroke",
                action: { viewModel.undo() }
            )
            .disabled(!viewModel.canUndo)
            .opacity(viewModel.canUndo ? 1 : 0.4)

            OButton(
                "Recognise",
                icon: "wand.and.stars",
                style: .primary,
                isLoading: viewModel.isRecognizing,
                isDisabled: !viewModel.canRecognize
            ) {
                Task { await viewModel.recognize() }
            }

            OIconButton(
                "trash",
                accessibilityLabel: "Clear canvas",
                style: .destructive,
                action: { viewModel.clear() }
            )
            .disabled(viewModel.strokes.isEmpty)
            .opacity(viewModel.strokes.isEmpty ? 0.4 : 1)
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 16)
    }

    // MARK: Alert helpers

    private var alertIsPresented: Binding<Bool> {
        Binding(
            get: {
                if case .failure = viewModel.drawState { return true }
                return false
            },
            set: { if !$0 { viewModel.resetState() } }
        )
    }

    private var alertError: RecognitionError? {
        if case .failure(let error) = viewModel.drawState { return error }
        return nil
    }

    /// A hashable token that changes whenever drawState transitions.
    private var drawStateVersion: Int {
        switch viewModel.drawState {
        case .idle:         return 0
        case .recognizing:  return 1
        case .success:      return 2
        case .failure:      return 3
        }
    }
}

// MARK: - Preview

#Preview("Draw Screen") {
    NavigationStack {
        DrawView(viewModel: DrawViewModel(service: MockRecognitionService.preview))
    }
    .preferredColorScheme(.dark)
}
