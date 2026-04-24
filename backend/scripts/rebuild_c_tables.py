"""
重建 C 端数据表（删除旧表 + 创建新表）
"""
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from load_env import load_environment
load_environment()

from sqlalchemy import create_engine, text
from config import Config

def rebuild_c_tables():
    """重建 C 端数据表"""
    print("=" * 60)
    print("🔧 开始重建 C 端数据表...")
    print("=" * 60)
    
    # 创建数据库引擎
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    
    # 完整的建表 SQL（包含 DROP 和 CREATE）
    sql_script = """
-- ============================
-- 1. C 端患者 / 线索表
-- ============================

DROP TABLE IF EXISTS public.c_messages CASCADE;
DROP TABLE IF EXISTS public.c_conversations CASCADE;
DROP TABLE IF EXISTS public.c_reports CASCADE;
DROP TABLE IF EXISTS public.c_health_records CASCADE;
DROP TABLE IF EXISTS public.c_patients CASCADE;

CREATE TABLE public.c_patients (
    id                      SERIAL PRIMARY KEY,
    patient_code            VARCHAR(50) UNIQUE,
    name                    VARCHAR(50),
    phone                   VARCHAR(20) UNIQUE,
    wechat_openid           VARCHAR(100) UNIQUE,
    wechat_unionid          VARCHAR(100),
    wechat_id               VARCHAR(50),
    
    source_channel          VARCHAR(50)  DEFAULT 'unknown',
    campaign_code           VARCHAR(50),
    entry_url               VARCHAR(255),
    lead_status             VARCHAR(20)  DEFAULT 'new',
    lead_stage_notes        TEXT,
    assigned_manager_id     INTEGER REFERENCES public.users(id),
    
    first_visit_at          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity_at        TIMESTAMP WITH TIME ZONE,
    
    status                  VARCHAR(20)  DEFAULT 'active',
    is_contacted            BOOLEAN      DEFAULT FALSE,
    
    created_at              TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_c_patients_lead_status ON public.c_patients (lead_status);
CREATE INDEX idx_c_patients_source_channel ON public.c_patients (source_channel);
CREATE INDEX idx_c_patients_campaign ON public.c_patients (campaign_code);
CREATE INDEX idx_c_patients_last_activity ON public.c_patients (last_activity_at);

-- ============================
-- 2. C 端会话表
-- ============================

CREATE TABLE public.c_conversations (
    id                      SERIAL PRIMARY KEY,
    lead_id                 INTEGER REFERENCES public.c_patients(id) ON DELETE CASCADE,
    session_id              VARCHAR(100) UNIQUE,
    
    status                  VARCHAR(20)  DEFAULT 'active',
    start_time              TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time                TIMESTAMP WITH TIME ZONE,
    last_message_at         TIMESTAMP WITH TIME ZONE,
    
    channel                 VARCHAR(50)  DEFAULT 'web',
    collected_data          JSONB,
    summary                 TEXT,
    keywords                TEXT,
    
    created_at              TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_c_conversations_lead ON public.c_conversations (lead_id);
CREATE INDEX idx_c_conversations_status ON public.c_conversations (status);
CREATE INDEX idx_c_conversations_channel ON public.c_conversations (channel);

-- ============================
-- 3. C 端消息表
-- ============================

CREATE TABLE public.c_messages (
    id                      SERIAL PRIMARY KEY,
    conversation_id         INTEGER REFERENCES public.c_conversations(id) ON DELETE CASCADE,
    
    role                    VARCHAR(20)  NOT NULL,
    content                 TEXT         NOT NULL,
    intent                  VARCHAR(50),
    
    channel                 VARCHAR(50)  DEFAULT 'web',
    metadata                JSONB,
    
    created_at              TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_c_messages_conversation ON public.c_messages (conversation_id);
CREATE INDEX idx_c_messages_role ON public.c_messages (role);
CREATE INDEX idx_c_messages_created ON public.c_messages (created_at);

-- ============================
-- 4. C 端健康记录表（保持不变）
-- ============================

CREATE TABLE public.c_health_records (
    id                      SERIAL PRIMARY KEY,
    patient_id              INTEGER REFERENCES public.c_patients(id) ON DELETE CASCADE,
    record_code             VARCHAR(50) UNIQUE,
    
    age                     INTEGER,
    gender                  VARCHAR(10)  DEFAULT 'female',
    
    birads_level            VARCHAR(10),
    nodule_size             VARCHAR(50),
    nodule_count            INTEGER      DEFAULT 1,
    nodule_location         VARCHAR(50),
    
    shape                   VARCHAR(50),
    boundary                VARCHAR(50),
    blood_flow              VARCHAR(50),
    echo_feature            VARCHAR(50),
    calcification           VARCHAR(50),
    elasticity_score        VARCHAR(50),
    
    symptoms                TEXT[],
    symptom_duration        VARCHAR(50),
    symptom_severity        VARCHAR(20),
    
    menstrual_status        VARCHAR(50),
    menstrual_cycle         VARCHAR(50),
    menstrual_regularity    VARCHAR(20),
    last_period_date        DATE,
    
    family_history          TEXT,
    family_risk_level       VARCHAR(20),
    genetic_history         TEXT,
    
    exam_history            TEXT[],
    previous_diagnosis      TEXT,
    treatment_history       TEXT,
    follow_up_status        VARCHAR(50),
    
    lifestyle               JSONB,
    psychological_status    VARCHAR(50),
    
    created_at              TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_c_health_records_patient ON public.c_health_records (patient_id);
CREATE INDEX idx_c_health_records_birads ON public.c_health_records (birads_level);

-- ============================
-- 5. C 端报告表
-- ============================

CREATE TABLE public.c_reports (
    id                      SERIAL PRIMARY KEY,
    lead_id                 INTEGER REFERENCES public.c_patients(id) ON DELETE CASCADE,
    conversation_id         INTEGER REFERENCES public.c_conversations(id),
    record_id               INTEGER REFERENCES public.c_health_records(id),
    
    report_code             VARCHAR(50) UNIQUE,
    report_html             TEXT,
    report_data             JSONB,
    
    download_token          VARCHAR(100) UNIQUE,
    status                  VARCHAR(20)  DEFAULT 'completed',
    
    generated_at            TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_download_at        TIMESTAMP WITH TIME ZONE,
    
    created_at              TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_c_reports_lead ON public.c_reports (lead_id);
CREATE INDEX idx_c_reports_conversation ON public.c_reports (conversation_id);
CREATE INDEX idx_c_reports_token ON public.c_reports (download_token);
CREATE INDEX idx_c_reports_status ON public.c_reports (status);

-- ============================
-- 完成
-- ============================
    """
    
    print("\n📝 开始执行 SQL 脚本...\n")
    
    try:
        with engine.connect() as conn:
            # 执行整个脚本
            conn.execute(text(sql_script))
            conn.commit()
        
        print("\n" + "=" * 60)
        print("✅ C 端数据表重建成功！")
        print("=" * 60)
        print("\n创建的表:")
        print("  ✓ c_patients (18 个字段)")
        print("  ✓ c_conversations (10 个字段)")
        print("  ✓ c_messages (7 个字段)")
        print("  ✓ c_health_records (34 个字段)")
        print("  ✓ c_reports (11 个字段)")
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    confirm = input("\n⚠️  警告：此操作将删除所有 C 端表的数据！\n是否继续？(yes/no): ")
    if confirm.lower() == 'yes':
        rebuild_c_tables()
    else:
        print("\n❌ 操作已取消")

