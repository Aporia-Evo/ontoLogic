// MARK: - UserDefaultsRepository.swift
// Lightweight UserDefaults-backed persistence for history and favourites.
// Replace with a CoreData or SwiftData implementation by swapping the
// concrete type at the injection root — protocol interfaces remain the same.

import Foundation

// MARK: - UserDefaultsHistoryRepository

final class UserDefaultsHistoryRepository: HistoryRepositoryProtocol {

    private let key = "onto_history"
    private let defaults: UserDefaults

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    func fetchAll() -> [HistoryEntry] {
        guard
            let data = defaults.data(forKey: key),
            let entries = try? JSONDecoder().decode([HistoryEntry].self, from: data)
        else { return [] }
        return entries
    }

    func fetchSorted() -> [HistoryEntry] {
        fetchAll().sorted { $0.date > $1.date }
    }

    func save(_ entity: HistoryEntry) {
        var all = fetchAll()
        // Replace if exists, otherwise prepend
        if let idx = all.firstIndex(where: { $0.id == entity.id }) {
            all[idx] = entity
        } else {
            all.insert(entity, at: 0)
        }
        persist(all)
    }

    func delete(id: UUID) {
        let filtered = fetchAll().filter { $0.id != id }
        persist(filtered)
    }

    func deleteAll() {
        defaults.removeObject(forKey: key)
    }

    private func persist(_ entries: [HistoryEntry]) {
        if let data = try? JSONEncoder().encode(entries) {
            defaults.set(data, forKey: key)
        }
    }
}

// MARK: - UserDefaultsFavouritesRepository

final class UserDefaultsFavouritesRepository: FavouritesRepositoryProtocol {

    private let key = "onto_favourites"
    private let defaults: UserDefaults

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    func fetchAll() -> [SymbolDetail] {
        guard
            let data = defaults.data(forKey: key),
            let items = try? JSONDecoder().decode([SymbolDetail].self, from: data)
        else { return [] }
        return items
    }

    func add(_ detail: SymbolDetail) {
        guard !contains(id: detail.id) else { return }
        var all = fetchAll()
        all.append(detail)
        persist(all)
    }

    func remove(id: UUID) {
        let filtered = fetchAll().filter { $0.id != id }
        persist(filtered)
    }

    func contains(id: UUID) -> Bool {
        fetchAll().contains { $0.id == id }
    }

    private func persist(_ items: [SymbolDetail]) {
        if let data = try? JSONEncoder().encode(items) {
            defaults.set(data, forKey: key)
        }
    }
}
