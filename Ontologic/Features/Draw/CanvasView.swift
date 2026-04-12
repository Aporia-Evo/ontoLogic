// MARK: - CanvasView.swift
// UIViewRepresentable wrapper that provides a drawing surface using UIKit.
// Strokes are stored as arrays of CGPoint paths, enabling undo and
// snapshot export for the recognition request.

import SwiftUI
import UIKit

// MARK: - Stroke model

/// A single continuous pen stroke.
struct Stroke {
    var points: [CGPoint] = []
    var color: UIColor = .white
    var lineWidth: CGFloat = 3.0
}

// MARK: - CanvasView

/// SwiftUI wrapper around a UIKit drawing canvas.
struct CanvasView: UIViewRepresentable {

    /// All committed strokes (read from parent)
    @Binding var strokes: [Stroke]
    /// The stroke currently being drawn
    @Binding var activeStroke: Stroke?

    var strokeColor: UIColor = .white
    var lineWidth: CGFloat = 3.0

    // MARK: UIViewRepresentable

    func makeCoordinator() -> Coordinator {
        Coordinator(strokes: $strokes, activeStroke: $activeStroke,
                    strokeColor: strokeColor, lineWidth: lineWidth)
    }

    func makeUIView(context: Context) -> CanvasUIView {
        let view = CanvasUIView()
        view.backgroundColor = UIColor(Color.ontoSurface_fallback())
        view.delegate = context.coordinator
        return view
    }

    func updateUIView(_ uiView: CanvasUIView, context: Context) {
        context.coordinator.strokeColor = strokeColor
        context.coordinator.lineWidth   = lineWidth
        uiView.strokes       = strokes
        uiView.activeStroke  = activeStroke
        uiView.setNeedsDisplay()
    }

    // MARK: Snapshot

    /// Renders all strokes into a UIImage at the given size.
    static func snapshot(strokes: [Stroke], size: CGSize) -> UIImage {
        let renderer = UIGraphicsImageRenderer(size: size)
        return renderer.image { ctx in
            UIColor(Color.ontoSurface_fallback()).setFill()
            ctx.fill(CGRect(origin: .zero, size: size))
            drawStrokes(strokes, in: ctx.cgContext)
        }
    }

    private static func drawStrokes(_ strokes: [Stroke], in context: CGContext) {
        for stroke in strokes {
            guard stroke.points.count > 1 else { continue }
            context.setStrokeColor(stroke.color.cgColor)
            context.setLineWidth(stroke.lineWidth)
            context.setLineCap(.round)
            context.setLineJoin(.round)
            context.beginPath()
            context.move(to: stroke.points[0])
            for point in stroke.points.dropFirst() {
                context.addLine(to: point)
            }
            context.strokePath()
        }
    }
}

// MARK: - Coordinator

extension CanvasView {
    final class Coordinator: NSObject, CanvasUIViewDelegate {

        @Binding var strokes: [Stroke]
        @Binding var activeStroke: Stroke?
        var strokeColor: UIColor
        var lineWidth: CGFloat

        init(
            strokes: Binding<[Stroke]>,
            activeStroke: Binding<Stroke?>,
            strokeColor: UIColor,
            lineWidth: CGFloat
        ) {
            _strokes      = strokes
            _activeStroke = activeStroke
            self.strokeColor = strokeColor
            self.lineWidth   = lineWidth
        }

        func canvasDidBeginStroke(at point: CGPoint) {
            activeStroke = Stroke(
                points: [point],
                color: strokeColor,
                lineWidth: lineWidth
            )
        }

        func canvasDidContinueStroke(to point: CGPoint) {
            activeStroke?.points.append(point)
        }

        func canvasDidEndStroke() {
            if let stroke = activeStroke {
                strokes.append(stroke)
            }
            activeStroke = nil
        }
    }
}

// MARK: - CanvasUIView

protocol CanvasUIViewDelegate: AnyObject {
    func canvasDidBeginStroke(at point: CGPoint)
    func canvasDidContinueStroke(to point: CGPoint)
    func canvasDidEndStroke()
}

final class CanvasUIView: UIView {

    weak var delegate: CanvasUIViewDelegate?
    var strokes: [Stroke] = []
    var activeStroke: Stroke? = nil

    override func draw(_ rect: CGRect) {
        guard let context = UIGraphicsGetCurrentContext() else { return }

        // Draw committed strokes
        for stroke in strokes {
            drawStroke(stroke, in: context)
        }
        // Draw active stroke
        if let active = activeStroke {
            drawStroke(active, in: context)
        }
    }

    private func drawStroke(_ stroke: Stroke, in context: CGContext) {
        guard stroke.points.count > 1 else { return }
        context.setStrokeColor(stroke.color.cgColor)
        context.setLineWidth(stroke.lineWidth)
        context.setLineCap(.round)
        context.setLineJoin(.round)
        context.beginPath()
        context.move(to: stroke.points[0])
        for point in stroke.points.dropFirst() {
            context.addLine(to: point)
        }
        context.strokePath()
    }

    // MARK: Touch handling

    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let point = touches.first?.location(in: self) else { return }
        delegate?.canvasDidBeginStroke(at: point)
    }

    override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let point = touches.first?.location(in: self) else { return }
        delegate?.canvasDidContinueStroke(to: point)
        setNeedsDisplay()
    }

    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        delegate?.canvasDidEndStroke()
        setNeedsDisplay()
    }

    override func touchesCancelled(_ touches: Set<UITouch>, with event: UIEvent?) {
        delegate?.canvasDidEndStroke()
        setNeedsDisplay()
    }
}
