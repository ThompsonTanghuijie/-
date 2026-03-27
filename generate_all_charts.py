import os
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

# =========================
# 1. matplotlib 中文设置
# =========================
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# =========================
# 2. 数据库连接配置
# =========================
username = "root"
password = "********"
host = "127.0.0.1"
port = 3306
database = "ecommerce_dw"

engine = create_engine(
    f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}?charset=utf8mb4"
)

# =========================
# 3. 输出目录
# =========================
output_dir = "charts"
os.makedirs(output_dir, exist_ok=True)


def save_line_chart(df, x_col, y_col, title, xlabel, ylabel, filename):
    plt.figure(figsize=(10, 5))
    plt.plot(df[x_col], df[y_col], marker="o")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, filename), dpi=150)
    plt.close()
    print(f"已生成：{filename}")


def save_bar_chart(df, x_col, y_col, title, xlabel, ylabel, filename):
    plt.figure(figsize=(8, 5))
    plt.bar(df[x_col], df[y_col])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, filename), dpi=150)
    plt.close()
    print(f"已生成：{filename}")


def save_barh_chart(df, x_col, y_col, title, xlabel, ylabel, filename):
    plt.figure(figsize=(10, 6))
    plt.barh(df[y_col], df[x_col])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, filename), dpi=150)
    plt.close()
    print(f"已生成：{filename}")


def plot_gmv_trend():
    sql = """
    SELECT
        stat_date,
        paid_order_amount AS daily_gmv
    FROM dws_order_day
    ORDER BY stat_date;
    """
    df = pd.read_sql(sql, engine)
    print("GMV趋势数据：")
    print(df.head())
    save_line_chart(
        df, "stat_date", "daily_gmv",
        "GMV趋势图", "日期", "GMV", "gmv_trend.png"
    )


def plot_dau_trend():
    sql = """
    SELECT
        event_date AS stat_date,
        COUNT(*) AS dau
    FROM dws_user_day
    GROUP BY event_date
    ORDER BY stat_date;
    """
    df = pd.read_sql(sql, engine)
    print("DAU趋势数据：")
    print(df.head())
    save_line_chart(
        df, "stat_date", "dau",
        "DAU趋势图", "日期", "DAU", "dau_trend.png"
    )


def plot_new_user_trend():
    sql = """
    SELECT
        DATE(register_time) AS stat_date,
        COUNT(*) AS new_user_count
    FROM users
    GROUP BY DATE(register_time)
    ORDER BY stat_date;
    """
    df = pd.read_sql(sql, engine)
    print("新增用户趋势数据：")
    print(df.head())
    save_line_chart(
        df, "stat_date", "new_user_count",
        "新增用户趋势图", "日期", "新增用户数", "new_user_trend.png"
    )


def plot_pay_conversion_trend():
    sql = """
    SELECT
        stat_date,
        ROUND(
            CASE
                WHEN order_cnt = 0 THEN 0
                ELSE paid_order_cnt * 100.0 / order_cnt
            END,
            2
        ) AS pay_conversion_rate
    FROM dws_order_day
    ORDER BY stat_date;
    """
    df = pd.read_sql(sql, engine)
    print("支付转化率趋势数据：")
    print(df.head())
    save_line_chart(
        df, "stat_date", "pay_conversion_rate",
        "支付转化率趋势图", "日期", "支付转化率(%)", "pay_conversion_trend.png"
    )


def plot_funnel_chart():
    sql = """
    SELECT '浏览' AS stage, COUNT(DISTINCT user_id) AS user_count
    FROM user_events
    WHERE event_type = 'view'

    UNION ALL

    SELECT '加购' AS stage, COUNT(DISTINCT user_id) AS user_count
    FROM user_events
    WHERE event_type = 'cart'

    UNION ALL

    SELECT '下单' AS stage, COUNT(DISTINCT user_id) AS user_count
    FROM user_events
    WHERE event_type = 'order'

    UNION ALL

    SELECT '支付' AS stage, COUNT(DISTINCT user_id) AS user_count
    FROM user_events
    WHERE event_type = 'pay';
    """
    df = pd.read_sql(sql, engine)
    print("漏斗图数据：")
    print(df)

    plt.figure(figsize=(8, 5))
    plt.bar(df["stage"], df["user_count"])
    plt.title("用户转化漏斗图")
    plt.xlabel("阶段")
    plt.ylabel("用户数")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "funnel_chart.png"), dpi=150)
    plt.close()
    print("已生成：funnel_chart.png")


def plot_product_sales_qty_top10():
    sql = """
    SELECT
        product_name,
        SUM(sales_qty) AS total_sales_qty
    FROM dws_product_day
    GROUP BY product_name
    ORDER BY total_sales_qty DESC
    LIMIT 10;
    """
    df = pd.read_sql(sql, engine)
    print("商品销量Top10数据：")
    print(df)

    df = df.iloc[::-1]
    save_barh_chart(
        df, "total_sales_qty", "product_name",
        "商品销量Top10", "销量", "商品名称", "product_sales_qty_top10.png"
    )


def plot_product_sales_amount_top10():
    sql = """
    SELECT
        product_name,
        SUM(sales_amount) AS total_sales_amount
    FROM dws_product_day
    GROUP BY product_name
    ORDER BY total_sales_amount DESC
    LIMIT 10;
    """
    df = pd.read_sql(sql, engine)
    print("商品销售额Top10数据：")
    print(df)

    df = df.iloc[::-1]
    save_barh_chart(
        df, "total_sales_amount", "product_name",
        "商品销售额Top10", "销售额", "商品名称", "product_sales_amount_top10.png"
    )


def plot_channel_orders():
    sql = """
    SELECT
        source_channel,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY source_channel
    ORDER BY order_count DESC;
    """
    df = pd.read_sql(sql, engine)
    print("渠道下单分布数据：")
    print(df)
    save_bar_chart(
        df, "source_channel", "order_count",
        "渠道下单分布图", "渠道", "订单数", "channel_orders.png"
    )


def main():
    print("开始生成全部图表...")
    plot_gmv_trend()
    plot_dau_trend()
    plot_new_user_trend()
    plot_pay_conversion_trend()
    plot_funnel_chart()
    plot_product_sales_qty_top10()
    plot_product_sales_amount_top10()
    plot_channel_orders()
    print(f"全部图表已生成，保存在目录：{output_dir}")


if __name__ == "__main__":
    main()