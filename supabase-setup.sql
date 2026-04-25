-- Supabase SQL Setup for Hello World Project
-- 在 Supabase Dashboard 的 SQL Editor 中执行此脚本

-- ============================================
-- 创建消息表
-- ============================================

-- 删除已存在的表（如果需要重新创建）
-- DROP TABLE IF EXISTS messages;

-- 创建消息表
CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    user_message TEXT NOT NULL,
    ai_message TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 为 ORDER BY 创建索引，避免大表全表扫描
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages (created_at DESC);

-- ============================================
-- 启用 Row Level Security
-- ============================================

ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- 允许所有人插入消息
CREATE POLICY "Allow public insert" ON messages
    FOR INSERT WITH CHECK (true);

-- 允许所有人查看消息
CREATE POLICY "Allow public select" ON messages
    FOR SELECT USING (true);

-- 允许所有人更新消息
CREATE POLICY "Allow public update" ON messages
    FOR UPDATE USING (true);

-- 允许所有人删除消息
CREATE POLICY "Allow public delete" ON messages
    FOR DELETE USING (true);

-- ============================================
-- 验证设置
-- ============================================

-- 查看表结构
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'messages';

-- 查看RLS策略
SELECT policyname, cmd, qual FROM pg_policies WHERE tablename = 'messages';
