import type { BookStudioClient } from '../api/restClient'

export type SaveCategory = 'structure' | 'panel' | 'text' | 'page' | 'edition'

export type SaveStatus = 'idle' | 'saving' | 'saved' | 'error'

type EntityType = 'panels' | 'pages' | 'edition'

interface DirtyEntry {
  entityType: EntityType
  entityId: string
  changes: Record<string, unknown>
  category: SaveCategory
}

const DEBOUNCE_MS: Record<SaveCategory, number> = {
  structure: 0,
  panel: 1000,
  text: 2000,
  page: 1000,
  edition: 2000,
}

const MAX_RETRIES = 3
const SAVED_DISPLAY_MS = 3000

interface SaveManagerConfig {
  client: BookStudioClient
  getBookId: () => string | null
  getEditionId: () => string | null
  getPageIdForPanel: (panelId: string) => string | null
  isNewUnsaved: () => boolean
}

export class SaveManager {
  private dirty = new Map<string, DirtyEntry>()
  private timers = new Map<string, ReturnType<typeof setTimeout>>()
  private status: SaveStatus = 'idle'
  private listeners = new Set<(status: SaveStatus) => void>()
  private activeSaves = 0
  private savedTimer: ReturnType<typeof setTimeout> | null = null
  private config: SaveManagerConfig

  constructor(config: SaveManagerConfig) {
    this.config = config
    this.handleOnline = this.handleOnline.bind(this)
    if (typeof window !== 'undefined') {
      window.addEventListener('online', this.handleOnline)
    }
  }

  dispose() {
    for (const timer of this.timers.values()) clearTimeout(timer)
    this.timers.clear()
    if (this.savedTimer) clearTimeout(this.savedTimer)
    if (typeof window !== 'undefined') {
      window.removeEventListener('online', this.handleOnline)
    }
  }

  enqueue(
    entityType: EntityType,
    entityId: string,
    changes: Record<string, unknown>,
    category: SaveCategory,
  ) {
    if (this.config.isNewUnsaved()) return

    const key = `${entityType}:${entityId}`
    const existing = this.dirty.get(key)
    if (existing) {
      Object.assign(existing.changes, changes)
    } else {
      this.dirty.set(key, { entityType, entityId, changes: { ...changes }, category })
    }

    // Reset debounce timer
    const existingTimer = this.timers.get(key)
    if (existingTimer) clearTimeout(existingTimer)

    const delay = DEBOUNCE_MS[category]
    if (delay === 0) {
      this.saveEntry(key)
    } else {
      this.timers.set(key, setTimeout(() => {
        this.timers.delete(key)
        this.saveEntry(key)
      }, delay))
    }
  }

  async flush(): Promise<void> {
    // Clear all pending timers and save immediately
    for (const [key, timer] of this.timers.entries()) {
      clearTimeout(timer)
      this.timers.delete(key)
    }
    const promises = [...this.dirty.keys()].map((key) => this.saveEntry(key))
    await Promise.allSettled(promises)
  }

  hasPendingChanges(): boolean {
    return this.dirty.size > 0 || this.activeSaves > 0
  }

  getStatus(): SaveStatus {
    return this.status
  }

  onStatusChange(cb: (status: SaveStatus) => void): () => void {
    this.listeners.add(cb)
    return () => this.listeners.delete(cb)
  }

  private setStatus(status: SaveStatus) {
    this.status = status
    for (const cb of this.listeners) cb(status)
  }

  private async saveEntry(key: string, retryCount = 0): Promise<void> {
    const entry = this.dirty.get(key)
    if (!entry) return

    const changes = { ...entry.changes }
    this.dirty.delete(key)
    this.activeSaves++
    this.setStatus('saving')

    try {
      await this.sendToApi(entry.entityType, entry.entityId, changes)
      this.activeSaves--
      if (this.activeSaves === 0 && this.dirty.size === 0) {
        this.setStatus('saved')
        if (this.savedTimer) clearTimeout(this.savedTimer)
        this.savedTimer = setTimeout(() => {
          if (this.status === 'saved') this.setStatus('idle')
        }, SAVED_DISPLAY_MS)
      }
    } catch (err) {
      this.activeSaves--
      if (retryCount < MAX_RETRIES) {
        // Re-enqueue with exponential backoff
        const backoff = Math.pow(2, retryCount) * 1000
        this.dirty.set(key, { ...entry, changes })
        this.timers.set(key, setTimeout(() => {
          this.timers.delete(key)
          this.saveEntry(key, retryCount + 1)
        }, backoff))
      } else {
        this.setStatus('error')
        console.error('[SaveManager] 최종 저장 실패:', entry.entityType, entry.entityId, err)
      }
    }
  }

  retryFailed() {
    if (this.status !== 'error') return
    // Re-trigger any remaining dirty entries
    for (const key of this.dirty.keys()) {
      this.saveEntry(key)
    }
  }

  private async sendToApi(
    entityType: EntityType,
    entityId: string,
    changes: Record<string, unknown>,
  ) {
    const { client, getBookId, getEditionId, getPageIdForPanel } = this.config

    switch (entityType) {
      case 'panels': {
        const pageId = getPageIdForPanel(entityId)
        if (!pageId) throw new Error(`Panel ${entityId}의 페이지를 찾을 수 없음`)
        await client.panels.update(pageId, entityId, changes)
        break
      }
      case 'pages': {
        const bookId = getBookId()
        const editionId = getEditionId()
        if (!bookId || !editionId) throw new Error('Book/Edition ID 없음')
        await client.pages.update(bookId, editionId, entityId, changes)
        break
      }
      case 'edition': {
        const bookId = getBookId()
        if (!bookId) throw new Error('Book ID 없음')
        await client.editions.update(bookId, entityId, changes)
        break
      }
    }
  }

  private handleOnline() {
    if (this.dirty.size > 0) {
      for (const key of this.dirty.keys()) {
        if (!this.timers.has(key)) {
          this.saveEntry(key)
        }
      }
    }
  }
}
