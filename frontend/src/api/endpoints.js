import api from './axios';

// This function now points exactly to your Django 'test' app view
export const fetchData = async () => {
    try {
        const response = await api.get('/api/data-endpoint/'); 
        return response.data; // This will be your list of id/name objects
    } catch (error) {
        console.error("API Error - Could not reach Django:", error);
    }
};

export const createItem = async (itemData) => {
    try {
        const response = await api.post('/api/items/', itemData);
        return response.data;
    } catch (error) {
        console.error("POST Error:", error);
        throw error;
    }
};