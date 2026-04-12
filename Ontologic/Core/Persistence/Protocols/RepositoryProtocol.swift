// MARK: - RepositoryProtocol.swift
// Generic persistence contract.
// Feature-specific repositories specialise this protocol.

import Foundation

/// A basic CRUD repository for `Identifiable & Codable` entities.
protocol RepositoryProtocol {
    associatedtype Entity: Identifiable & Codable

    func fetchAll() -> [Entity]
    func save(_ entity: Entity)
    func delete(id: Entity.ID)
    func deleteAll()
}

// MARK: - HistoryRepositoryProtocol

protocol HistoryRepositoryProtocol: RepositoryProtocol where Entity == HistoryEntry {
    /// Returns entries sorted newest-first.
    func fetchSorted() -> [HistoryEntry]
}

// MARK: - FavouritesRepositoryProtocol

protocol FavouritesRepositoryProtocol {
    func fetchAll() -> [SymbolDetail]
    func add(_ detail: SymbolDetail)
    func remove(id: UUID)
    func contains(id: UUID) -> Bool
}
