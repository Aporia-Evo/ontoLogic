// MARK: - SettingsView.swift

import SwiftUI

struct SettingsView: View {

    @StateObject var viewModel: SettingsViewModel
    @State private var showResetConfirm = false

    var body: some View {
        ZStack {
            Color.ontoBackground_fallback().ignoresSafeArea()

            List {

                // MARK: Drawing
                Section {
                    VStack(alignment: .leading, spacing: 6) {
                        HStack {
                            Text("Stroke Width")
                                .font(.ontoBodyLarge)
                                .foregroundColor(.ontoTextPrimary_fallback())
                            Spacer()
                            Text(String(format: "%.1f pt", viewModel.strokeWidth))
                                .font(.ontoMono)
                                .foregroundColor(.ontoTextSecondary_fallback())
                        }
                        Slider(value: $viewModel.strokeWidth, in: 1...8, step: 0.5)
                            .tint(.ontoPrimary_fallback())
                    }
                    .padding(.vertical, 4)

                    Toggle(isOn: $viewModel.hapticFeedbackEnabled) {
                        Label("Haptic Feedback", systemImage: "hand.tap")
                            .foregroundColor(.ontoTextPrimary_fallback())
                    }
                    .tint(.ontoPrimary_fallback())
                } header: {
                    Text("Drawing").ontoSectionHeader()
                }
                .listRowBackground(Color.ontoSurface_fallback())

                // MARK: Recognition
                Section {
                    Toggle(isOn: $viewModel.autoRecognize) {
                        VStack(alignment: .leading, spacing: 2) {
                            Label("Auto-Recognise", systemImage: "wand.and.stars")
                                .foregroundColor(.ontoTextPrimary_fallback())
                            Text("Automatically recognise after a short pause")
                                .font(.ontoBodySmall)
                                .foregroundColor(.ontoTextSecondary_fallback())
                        }
                    }
                    .tint(.ontoPrimary_fallback())
                } header: {
                    Text("Recognition").ontoSectionHeader()
                }
                .listRowBackground(Color.ontoSurface_fallback())

                // MARK: About
                Section {
                    LabeledContent("Version", value: viewModel.appVersion)
                        .foregroundColor(.ontoTextPrimary_fallback())
                    LabeledContent("Build", value: viewModel.buildNumber)
                        .foregroundColor(.ontoTextPrimary_fallback())
                } header: {
                    Text("About").ontoSectionHeader()
                }
                .listRowBackground(Color.ontoSurface_fallback())

                // MARK: Reset
                Section {
                    Button(role: .destructive) {
                        showResetConfirm = true
                    } label: {
                        Label("Reset to Defaults", systemImage: "arrow.counterclockwise")
                    }
                }
                .listRowBackground(Color.ontoSurface_fallback())
            }
            .listStyle(.insetGrouped)
            .scrollContentBackground(.hidden)
        }
        .navigationTitle("Settings")
        .navigationBarTitleDisplayMode(.large)
        .confirmationDialog(
            "Reset all settings to defaults?",
            isPresented: $showResetConfirm,
            titleVisibility: .visible
        ) {
            Button("Reset", role: .destructive) { viewModel.resetToDefaults() }
            Button("Cancel", role: .cancel) {}
        }
    }
}

// MARK: - Preview

#Preview {
    NavigationStack {
        SettingsView(viewModel: SettingsViewModel())
    }
    .preferredColorScheme(.dark)
}
