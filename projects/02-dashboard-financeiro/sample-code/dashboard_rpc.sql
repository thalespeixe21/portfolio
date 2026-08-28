-- PostgreSQL RPC functions for the financial dashboard
-- Called from the frontend via Supabase client
-- Both use SECURITY DEFINER to run with elevated privileges

-- 1. Historical monthly data (used for charts and trend analysis)
CREATE OR REPLACE FUNCTION fn_dashboard_monthly(
    p_start_date DATE DEFAULT '2025-01-01',
    p_end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    month TEXT,
    gross_revenue NUMERIC,
    net_revenue NUMERIC,
    total_expenses NUMERIC,
    marketing_spend NUMERIC,
    subscription_revenue NUMERIC,
    refund_total NUMERIC,
    chargeback_total NUMERIC,
    order_count INTEGER,
    roas NUMERIC,
    net_margin NUMERIC
) AS $$
    SELECT
        TO_CHAR(date_trunc('month', d.date), 'YYYY-MM') AS month,
        SUM(d.gross_revenue),
        SUM(d.net_revenue),
        SUM(d.total_expenses),
        SUM(d.marketing_spend),
        SUM(d.subscription_revenue),
        SUM(d.refund_total),
        SUM(d.chargeback_total),
        SUM(d.order_count)::INTEGER,
        -- ROAS = Net Revenue / Marketing Spend
        CASE WHEN SUM(d.marketing_spend) > 0
             THEN ROUND(SUM(d.net_revenue) / SUM(d.marketing_spend), 2)
             ELSE 0 END,
        -- Net Margin = (Net Revenue - Total Expenses) / Gross Revenue
        CASE WHEN SUM(d.gross_revenue) > 0
             THEN ROUND(
                 (SUM(d.net_revenue) - SUM(d.total_expenses))
                 / SUM(d.gross_revenue) * 100, 1)
             ELSE 0 END
    FROM daily_finance d
    WHERE d.date BETWEEN p_start_date AND p_end_date
    GROUP BY date_trunc('month', d.date)
    ORDER BY month;
$$ LANGUAGE sql SECURITY DEFINER;


-- 2. Current month data (used for hero KPIs and real-time metrics)
CREATE OR REPLACE FUNCTION fn_dashboard_current()
RETURNS TABLE (
    gross_revenue NUMERIC,
    net_revenue NUMERIC,
    total_expenses NUMERIC,
    marketing_spend NUMERIC,
    subscription_revenue NUMERIC,
    refund_total NUMERIC,
    order_count INTEGER,
    roas NUMERIC,
    net_margin NUMERIC,
    operating_profit NUMERIC,
    final_result NUMERIC,
    breakeven_roas NUMERIC,
    days_elapsed INTEGER,
    days_in_month INTEGER
) AS $$
DECLARE
    v_first_day DATE := date_trunc('month', CURRENT_DATE)::DATE;
    v_last_day DATE := (date_trunc('month', CURRENT_DATE) + INTERVAL '1 month - 1 day')::DATE;
BEGIN
    RETURN QUERY
    SELECT
        COALESCE(SUM(d.gross_revenue), 0),
        COALESCE(SUM(d.net_revenue), 0),
        COALESCE(SUM(d.total_expenses), 0),
        COALESCE(SUM(d.marketing_spend), 0),
        COALESCE(SUM(d.subscription_revenue), 0),
        COALESCE(SUM(d.refund_total), 0),
        COALESCE(SUM(d.order_count), 0)::INTEGER,
        -- ROAS
        CASE WHEN SUM(d.marketing_spend) > 0
             THEN ROUND(SUM(d.net_revenue) / SUM(d.marketing_spend), 2)
             ELSE 0 END,
        -- Net Margin
        CASE WHEN SUM(d.gross_revenue) > 0
             THEN ROUND(
                 (SUM(d.net_revenue) - SUM(d.total_expenses))
                 / SUM(d.gross_revenue) * 100, 1)
             ELSE 0 END,
        -- Operating Profit (before subscriptions)
        COALESCE(SUM(d.net_revenue) - SUM(d.total_expenses), 0),
        -- Final Result (after subscriptions)
        COALESCE(SUM(d.net_revenue) - SUM(d.total_expenses) + SUM(d.subscription_revenue), 0),
        -- Breakeven ROAS = Total Expenses / Marketing Spend
        CASE WHEN SUM(d.marketing_spend) > 0
             THEN ROUND(SUM(d.total_expenses) / SUM(d.marketing_spend), 2)
             ELSE 0 END,
        -- Days elapsed in current month
        (CURRENT_DATE - v_first_day + 1)::INTEGER,
        -- Total days in month
        (v_last_day - v_first_day + 1)::INTEGER
    FROM daily_finance d
    WHERE d.date BETWEEN v_first_day AND CURRENT_DATE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- Analytical views consumed by the dashboard

CREATE OR REPLACE VIEW vw_monthly_pnl AS
SELECT
    TO_CHAR(date_trunc('month', date), 'YYYY-MM') AS month,
    SUM(gross_revenue) AS gross_revenue,
    SUM(net_revenue) AS net_revenue,
    SUM(marketing_spend) AS marketing,
    SUM(payroll) AS payroll,
    SUM(software_costs) AS software,
    SUM(operations_costs) AS operations,
    SUM(total_expenses) AS total_expenses,
    SUM(net_revenue) - SUM(total_expenses) AS operating_profit,
    SUM(subscription_revenue) AS subscriptions,
    SUM(net_revenue) - SUM(total_expenses) + SUM(subscription_revenue) AS final_result
FROM daily_finance
GROUP BY date_trunc('month', date)
ORDER BY month;


CREATE OR REPLACE VIEW vw_refund_analysis AS
SELECT
    TO_CHAR(date_trunc('month', r.date), 'YYYY-MM') AS month,
    r.event_type,
    COUNT(*) AS event_count,
    SUM(r.amount_usd) AS total_usd,
    SUM(r.amount_brl) AS total_brl,
    ROUND(
        SUM(r.amount_usd) / NULLIF(
            (SELECT SUM(gross_revenue) FROM daily_finance df
             WHERE date_trunc('month', df.date) = date_trunc('month', r.date)), 0
        ) * 100, 2
    ) AS pct_of_gross
FROM refunds r
GROUP BY date_trunc('month', r.date), r.event_type
ORDER BY month DESC, event_type;
