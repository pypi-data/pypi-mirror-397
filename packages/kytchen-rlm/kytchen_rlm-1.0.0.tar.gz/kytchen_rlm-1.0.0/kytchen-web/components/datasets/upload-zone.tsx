'use client'

import { useCallback, useState } from 'react'
import { Upload, FileText, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const ALLOWED_EXTENSIONS = ['txt', 'json', 'csv', 'pdf', 'docx', 'xlsx', 'md']
const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

interface UploadZoneProps {
    workspaceId: string
    onUploadComplete?: (dataset: { id: string; name: string; status: string }) => void
    onError?: (error: string) => void
}

export function UploadZone({ workspaceId, onUploadComplete, onError }: UploadZoneProps) {
    const [isDragging, setIsDragging] = useState(false)
    const [isUploading, setIsUploading] = useState(false)
    const [selectedFile, setSelectedFile] = useState<File | null>(null)
    const [uploadProgress, setUploadProgress] = useState(0)

    const validateFile = (file: File): string | null => {
        const ext = file.name.split('.').pop()?.toLowerCase()
        if (!ext || !ALLOWED_EXTENSIONS.includes(ext)) {
            return `File type .${ext} not allowed. Allowed: ${ALLOWED_EXTENSIONS.join(', ')}`
        }
        if (file.size > MAX_FILE_SIZE) {
            return `File too large. Maximum size is 10MB.`
        }
        return null
    }

    const handleDrag = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setIsDragging(true)
        } else if (e.type === 'dragleave') {
            setIsDragging(false)
        }
    }, [])

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        setIsDragging(false)

        const files = e.dataTransfer.files
        if (files.length > 0) {
            const file = files[0]
            const error = validateFile(file)
            if (error) {
                onError?.(error)
                return
            }
            setSelectedFile(file)
        }
    }, [onError])

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files
        if (files && files.length > 0) {
            const file = files[0]
            const error = validateFile(file)
            if (error) {
                onError?.(error)
                return
            }
            setSelectedFile(file)
        }
    }

    const handleUpload = async () => {
        if (!selectedFile) return

        setIsUploading(true)
        setUploadProgress(0)

        try {
            const formData = new FormData()
            formData.append('file', selectedFile)
            formData.append('workspace_id', workspaceId)

            // Simulated progress (real progress requires XMLHttpRequest)
            const progressInterval = setInterval(() => {
                setUploadProgress(prev => Math.min(prev + 10, 90))
            }, 200)

            const response = await fetch('/api/datasets', {
                method: 'POST',
                body: formData,
            })

            clearInterval(progressInterval)
            setUploadProgress(100)

            if (!response.ok) {
                const data = await response.json()
                throw new Error(data.error || 'Upload failed')
            }

            const dataset = await response.json()
            onUploadComplete?.(dataset)
            setSelectedFile(null)
        } catch (err) {
            onError?.(err instanceof Error ? err.message : 'Upload failed')
        } finally {
            setIsUploading(false)
            setUploadProgress(0)
        }
    }

    const handleClear = () => {
        setSelectedFile(null)
    }

    return (
        <div className="space-y-4">
            {/* Drop Zone */}
            <div
                className={cn(
                    "border-2 border-dashed border-foreground p-12 text-center transition-all cursor-pointer",
                    isDragging && "bg-blue-tape/10 border-blue-tape",
                    isUploading && "opacity-50 pointer-events-none"
                )}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => document.getElementById('file-input')?.click()}
            >
                <input
                    id="file-input"
                    type="file"
                    className="hidden"
                    accept={ALLOWED_EXTENSIONS.map(ext => `.${ext}`).join(',')}
                    onChange={handleFileSelect}
                    disabled={isUploading}
                />
                <Upload className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p className="font-mono text-sm font-bold uppercase tracking-wide">
                    Drop files here or click to browse
                </p>
                <p className="font-mono text-xs opacity-60 mt-2">
                    {ALLOWED_EXTENSIONS.map(e => e.toUpperCase()).join(', ')} up to 10MB
                </p>
            </div>

            {/* Selected File Preview */}
            {selectedFile && (
                <div className="flex items-center justify-between border border-foreground p-4 bg-background shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                    <div className="flex items-center gap-4">
                        <div className="border border-foreground p-2 bg-surface-elevated">
                            <FileText className="w-6 h-6" />
                        </div>
                        <div>
                            <p className="font-mono text-sm font-bold">{selectedFile.name}</p>
                            <p className="font-mono text-xs text-muted-foreground">
                                {(selectedFile.size / 1024).toFixed(1)} KB
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        {!isUploading && (
                            <>
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    className="h-8 w-8"
                                    onClick={(e) => {
                                        e.stopPropagation()
                                        handleClear()
                                    }}
                                >
                                    <X className="w-4 h-4" />
                                </Button>
                                <Button
                                    onClick={(e) => {
                                        e.stopPropagation()
                                        handleUpload()
                                    }}
                                    className="font-mono uppercase text-xs"
                                >
                                    Upload
                                </Button>
                            </>
                        )}
                    </div>
                </div>
            )}

            {/* Upload Progress */}
            {isUploading && (
                <div className="space-y-2">
                    <div className="flex justify-between font-mono text-xs">
                        <span>Uploading...</span>
                        <span>{uploadProgress}%</span>
                    </div>
                    <div className="h-2 bg-stone-200 border border-foreground">
                        <div
                            className="h-full bg-blue-tape transition-all"
                            style={{ width: `${uploadProgress}%` }}
                        />
                    </div>
                </div>
            )}
        </div>
    )
}
