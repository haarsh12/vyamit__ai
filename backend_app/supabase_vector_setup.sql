-- 🚀 SUPABASE VECTOR DATABASE SETUP
-- Run these commands in Supabase SQL Editor

-- ✅ Step 1: Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ✅ Step 2: Add embedding column to existing item table
-- Using 384 dimensions for intfloat/multilingual-e5-small
ALTER TABLE item ADD COLUMN IF NOT EXISTS embedding vector(384);

-- ✅ Step 3: Add metadata column for better search (optional but powerful)
ALTER TABLE item ADD COLUMN IF NOT EXISTS search_metadata JSONB;

-- ✅ Step 4: Create vector index for fast similarity search
-- This is CRITICAL for performance with large datasets
CREATE INDEX IF NOT EXISTS item_embedding_idx 
ON item USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- ✅ Step 5: Create similarity search function
-- This function returns top N most similar items
CREATE OR REPLACE FUNCTION match_items(
    query_embedding vector(384),
    match_count int DEFAULT 15,
    similarity_threshold float DEFAULT 0.1
) 
RETURNS TABLE (
    id int,
    master_id text,
    names text,
    category text,
    price float,
    unit text,
    similarity float
) 
LANGUAGE sql 
AS $$
    SELECT 
        item.id,
        item.master_id,
        item.names,
        item.category,
        item.price,
        item.unit,
        1 - (item.embedding <=> query_embedding) as similarity
    FROM item
    WHERE item.embedding IS NOT NULL
        AND 1 - (item.embedding <=> query_embedding) > similarity_threshold
    ORDER BY item.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- ✅ Step 6: Create function to get embedding statistics
CREATE OR REPLACE FUNCTION get_embedding_stats()
RETURNS TABLE (
    total_items bigint,
    items_with_embeddings bigint,
    embedding_coverage_percent numeric
)
LANGUAGE sql
AS $$
    SELECT 
        COUNT(*) as total_items,
        COUNT(embedding) as items_with_embeddings,
        ROUND((COUNT(embedding)::numeric / COUNT(*)::numeric) * 100, 2) as embedding_coverage_percent
    FROM item;
$$;

-- ✅ Step 7: Create function to find similar items by ID
CREATE OR REPLACE FUNCTION find_similar_items(
    item_id int,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id int,
    master_id text,
    names text,
    similarity float
)
LANGUAGE sql
AS $$
    SELECT 
        i2.id,
        i2.master_id,
        i2.names,
        1 - (i1.embedding <=> i2.embedding) as similarity
    FROM item i1, item i2
    WHERE i1.id = item_id 
        AND i2.id != item_id
        AND i1.embedding IS NOT NULL 
        AND i2.embedding IS NOT NULL
    ORDER BY i1.embedding <=> i2.embedding
    LIMIT match_count;
$$;

-- ✅ Step 8: Add some sample data with multilingual names (if needed)
-- Uncomment and modify as needed
/*
INSERT INTO item (master_id, names, category, price, unit) VALUES
('RICE001', '["Chawal", "Rice", "चावल", "तांदूळ", "Basmati Rice"]', 'Anaaj', 80.0, 'kg'),
('TOMATO001', '["Tamatar", "Tomato", "टमाटर", "टोमॅटो"]', 'Sabzi', 25.0, 'kg'),
('ONION001', '["Pyaz", "Onion", "प्याज", "कांदा"]', 'Sabzi', 30.0, 'kg'),
('WHEAT001', '["Gehun", "Wheat", "गेहूं", "गहू"]', 'Anaaj', 45.0, 'kg'),
('SUGAR001', '["Cheeni", "Sugar", "चीनी", "साखर"]', 'Grocery', 42.0, 'kg');
*/

-- ✅ Step 9: Create indexes for better performance
CREATE INDEX IF NOT EXISTS item_category_idx ON item(category);
CREATE INDEX IF NOT EXISTS item_master_id_idx ON item(master_id);
CREATE INDEX IF NOT EXISTS item_price_idx ON item(price);

-- ✅ Step 10: Grant necessary permissions (if needed)
-- GRANT SELECT, INSERT, UPDATE ON item TO authenticated;
-- GRANT EXECUTE ON FUNCTION match_items TO authenticated;
-- GRANT EXECUTE ON FUNCTION get_embedding_stats TO authenticated;

-- 🎉 Setup complete! 
-- Now run the Python script to generate embeddings.