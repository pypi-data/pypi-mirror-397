export class KytchenError extends Error {
    constructor(message: string, public statusCode?: number, public code?: string) {
        super(message);
        this.name = 'KytchenError';
    }
}

export class AuthenticationError extends KytchenError {
    constructor(message: string = 'Invalid API key') {
        super(message, 401, 'authentication_error');
    }
}

export class NotFoundError extends KytchenError {
    constructor(message: string) {
        super(message, 404, 'not_found');
    }
}
