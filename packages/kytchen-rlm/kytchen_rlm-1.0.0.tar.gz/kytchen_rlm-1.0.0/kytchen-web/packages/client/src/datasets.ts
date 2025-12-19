import { KytchenClient } from './client';
import { Dataset, CreateDatasetParams } from './types';

export class Datasets {
    constructor(private client: KytchenClient) {}

    async create(params: CreateDatasetParams): Promise<Dataset> {
        const formData = new FormData();
        formData.append('name', params.name);
        formData.append('file', params.file);

        return this.client.request<Dataset>('/v1/datasets', {
            method: 'POST',
            body: formData,
            // Headers for FormData are usually handled automatically by fetch to set boundary
        });
    }

    async list(): Promise<Dataset[]> {
        return this.client.request<Dataset[]>('/v1/datasets');
    }

    async delete(id: string): Promise<void> {
        await this.client.request(`/v1/datasets/${id}`, {
            method: 'DELETE',
        });
    }
}
