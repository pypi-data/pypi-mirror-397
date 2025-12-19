import { KytchenClient } from '../src';

async function main() {
    const client = new KytchenClient({
        apiKey: process.env.KYTCHEN_API_KEY || 'kyt_test_key',
    });

    try {
        // Create Dataset
        // Note: In Node.js you might need polyfills for File/FormData or use specific Node methods
        // This example assumes browser-like environment or polyfills
        /*
        const dataset = await client.datasets.create({
            name: 'contracts',
            file: new File(['...'], 'contracts.pdf'),
        });
        console.log('Dataset created:', dataset.id);
        */

        const kytchenId = process.env.KYTCHEN_ID || 'kyt_123';

        // Create ticket
        const ticket = await client.tickets.create(kytchenId, {
            query: 'What are the indemnification terms?',
            dataset_ids: [],
        });

        console.log('Ticket created:', ticket.id);

        // Streaming
        console.log('Streaming ticket...');
        for await (const event of client.tickets.stream(kytchenId, {
            query: 'Explain the termination clause.',
        })) {
            console.log(event.type, event.data);
        }

    } catch (err) {
        console.error('Error:', err);
    }
}

main();
