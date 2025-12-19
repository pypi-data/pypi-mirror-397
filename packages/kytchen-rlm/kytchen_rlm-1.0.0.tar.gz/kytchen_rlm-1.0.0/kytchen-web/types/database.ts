export type Json =
    | string
    | number
    | boolean
    | null
    | { [key: string]: Json | undefined }
    | Json[]

export interface Database {
    public: {
        Tables: {
            workspaces: {
                Row: {
                    id: string
                    name: string
                    slug: string
                    plan: string
                    stripe_customer_id: string | null
                    created_at: string
                    updated_at: string
                }
                Insert: {
                    id?: string
                    name: string
                    slug: string
                    plan?: string
                    stripe_customer_id?: string | null
                    created_at?: string
                    updated_at?: string
                }
                Update: {
                    id?: string
                    name?: string
                    slug?: string
                    plan?: string
                    stripe_customer_id?: string | null
                    created_at?: string
                    updated_at?: string
                }
                Relationships: []
            }
            members: {
                Row: {
                    workspace_id: string
                    user_id: string
                    role: string
                    created_at: string
                }
                Insert: {
                    workspace_id: string
                    user_id: string
                    role?: string
                    created_at?: string
                }
                Update: {
                    workspace_id?: string
                    user_id?: string
                    role?: string
                    created_at?: string
                }
                Relationships: []
            }
            api_keys: {
                Row: {
                    id: string
                    workspace_id: string
                    key_hash: string
                    key_prefix: string
                    name: string | null
                    last_used_at: string | null
                    revoked_at: string | null
                    created_at: string
                }
                Insert: {
                    id?: string
                    workspace_id: string
                    key_hash: string
                    key_prefix: string
                    name?: string | null
                    last_used_at?: string | null
                    revoked_at?: string | null
                    created_at?: string
                }
                Update: {
                    id?: string
                    workspace_id?: string
                    key_hash?: string
                    key_prefix?: string
                    name?: string | null
                    last_used_at?: string | null
                    revoked_at?: string | null
                    created_at?: string
                }
                Relationships: []
            }
            datasets: {
                Row: {
                    id: string
                    workspace_id: string
                    name: string
                    description: string | null
                    storage_bucket: string
                    storage_path: string
                    size_bytes: number
                    content_hash: string
                    mime_type: string | null
                    status: string
                    processing_error: string | null
                    created_at: string
                    updated_at: string
                }
                Insert: {
                    id?: string
                    workspace_id: string
                    name: string
                    description?: string | null
                    storage_bucket?: string
                    storage_path: string
                    size_bytes: number
                    content_hash: string
                    mime_type?: string | null
                    status?: string
                    processing_error?: string | null
                    created_at?: string
                    updated_at?: string
                }
                Update: {
                    id?: string
                    workspace_id?: string
                    name?: string
                    description?: string | null
                    storage_bucket?: string
                    storage_path?: string
                    size_bytes?: number
                    content_hash?: string
                    mime_type?: string | null
                    status?: string
                    processing_error?: string | null
                    created_at?: string
                    updated_at?: string
                }
                Relationships: []
            }
            runs: {
                Row: {
                    id: string
                    workspace_id: string
                    api_key_id: string | null
                    dataset_ids: string[]
                    query: string
                    budget: Json
                    status: string
                    tool_session_id: string | null
                    answer: string | null
                    success: boolean | null
                    error: string | null
                    created_at: string
                    started_at: string | null
                    completed_at: string | null
                    e2b_sandbox_id: string | null
                    metrics: Json
                }
                Insert: {
                    id?: string
                    workspace_id: string
                    api_key_id?: string | null
                    dataset_ids?: string[]
                    query: string
                    budget?: Json
                    status?: string
                    tool_session_id?: string | null
                    answer?: string | null
                    success?: boolean | null
                    error?: string | null
                    created_at?: string
                    started_at?: string | null
                    completed_at?: string | null
                    e2b_sandbox_id?: string | null
                    metrics?: Json
                }
                Update: {
                    id?: string
                    workspace_id?: string
                    api_key_id?: string | null
                    dataset_ids?: string[]
                    query?: string
                    budget?: Json
                    status?: string
                    tool_session_id?: string | null
                    answer?: string | null
                    success?: boolean | null
                    error?: string | null
                    created_at?: string
                    started_at?: string | null
                    completed_at?: string | null
                    e2b_sandbox_id?: string | null
                    metrics?: Json
                }
                Relationships: []
            }
            evidence: {
                Row: {
                    id: string
                    workspace_id: string
                    run_id: string
                    tool_name: string
                    params: Json
                    dataset_id: string | null
                    snippet: string
                    line_start: number | null
                    line_end: number | null
                    note: string | null
                    created_at: string
                    e2b_execution_id: string | null
                    execution_time_ms: number | null
                }
                Insert: {
                    id?: string
                    workspace_id: string
                    run_id: string
                    tool_name: string
                    params?: Json
                    dataset_id?: string | null
                    snippet: string
                    line_start?: number | null
                    line_end?: number | null
                    note?: string | null
                    created_at?: string
                    e2b_execution_id?: string | null
                    execution_time_ms?: number | null
                }
                Update: {
                    id?: string
                    workspace_id?: string
                    run_id?: string
                    tool_name?: string
                    params?: Json
                    dataset_id?: string | null
                    snippet?: string
                    line_start?: number | null
                    line_end?: number | null
                    note?: string | null
                    created_at?: string
                    e2b_execution_id?: string | null
                    execution_time_ms?: number | null
                }
                Relationships: []
            }
            usage: {
                Row: {
                    workspace_id: string
                    month_start: string
                    storage_bytes: number
                    requests_this_month: number
                    egress_bytes_this_month: number
                    updated_at: string
                }
                Insert: {
                    workspace_id: string
                    month_start?: string
                    storage_bytes?: number
                    requests_this_month?: number
                    egress_bytes_this_month?: number
                    updated_at?: string
                }
                Update: {
                    workspace_id?: string
                    month_start?: string
                    storage_bytes?: number
                    requests_this_month?: number
                    egress_bytes_this_month?: number
                    updated_at?: string
                }
                Relationships: []
            }
            audit_logs: {
                Row: {
                    id: string
                    workspace_id: string
                    event_type: string
                    event_category: string
                    severity: string
                    actor_type: string
                    actor_id: string | null
                    actor_ip: string | null
                    user_agent: string | null
                    resource_type: string | null
                    resource_id: string | null
                    description: string
                    metadata: Json
                    content_hash: string
                    previous_hash: string | null
                    created_at: string
                }
                Insert: {
                    id?: string
                    workspace_id: string
                    event_type: string
                    event_category: string
                    severity?: string
                    actor_type: string
                    actor_id?: string | null
                    actor_ip?: string | null
                    user_agent?: string | null
                    resource_type?: string | null
                    resource_id?: string | null
                    description: string
                    metadata?: Json
                    content_hash: string
                    previous_hash?: string | null
                    created_at?: string
                }
                Update: {
                    id?: string
                    workspace_id?: string
                    event_type?: string
                    event_category?: string
                    severity?: string
                    actor_type?: string
                    actor_id?: string | null
                    actor_ip?: string | null
                    user_agent?: string | null
                    resource_type?: string | null
                    resource_id?: string | null
                    description?: string
                    metadata?: Json
                    content_hash?: string
                    previous_hash?: string | null
                    created_at?: string
                }
                Relationships: []
            }
            billing: {
                Row: {
                    workspace_id: string
                    stripe_customer_id: string | null
                    stripe_subscription_id: string | null
                    stripe_price_id: string | null
                    subscription_status: string | null
                    current_period_start: string | null
                    current_period_end: string | null
                    cancel_at_period_end: boolean | null
                    created_at: string
                    updated_at: string
                }
                Insert: {
                    workspace_id: string
                    stripe_customer_id?: string | null
                    stripe_subscription_id?: string | null
                    stripe_price_id?: string | null
                    subscription_status?: string | null
                    current_period_start?: string | null
                    current_period_end?: string | null
                    cancel_at_period_end?: boolean | null
                    created_at?: string
                    updated_at?: string
                }
                Update: {
                    workspace_id?: string
                    stripe_customer_id?: string | null
                    stripe_subscription_id?: string | null
                    stripe_price_id?: string | null
                    subscription_status?: string | null
                    current_period_start?: string | null
                    current_period_end?: string | null
                    cancel_at_period_end?: boolean | null
                    created_at?: string
                    updated_at?: string
                }
                Relationships: []
            }
            sandbox_sessions: {
                Row: {
                    id: string
                    workspace_id: string
                    run_id: string | null
                    e2b_sandbox_id: string
                    context_id: string
                    status: string
                    created_at: string
                    expires_at: string
                    metadata: Json
                }
                Insert: {
                    id?: string
                    workspace_id: string
                    run_id?: string | null
                    e2b_sandbox_id: string
                    context_id?: string
                    status?: string
                    created_at?: string
                    expires_at: string
                    metadata?: Json
                }
                Update: {
                    id?: string
                    workspace_id?: string
                    run_id?: string | null
                    e2b_sandbox_id?: string
                    context_id?: string
                    status?: string
                    created_at?: string
                    expires_at?: string
                    metadata?: Json
                }
                Relationships: []
            }
        }
        Views: {
            [_ in never]: never
        }
        Functions: {
            [_ in never]: never
        }
        Enums: {
            [_ in never]: never
        }
        CompositeTypes: {
            [_ in never]: never
        }
    }
}
