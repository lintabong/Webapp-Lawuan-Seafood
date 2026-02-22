
create or replace function create_order_full(
    p_customer_id bigint,
    p_created_by uuid,
    p_order_date timestamptz,
    p_status text,
    p_delivery_price numeric,
    p_delivery_type text,
    p_items jsonb
)
returns table (
    order_id bigint,
    transaction_id bigint,
    current_balance numeric
)
language plpgsql
as $$
declare
    v_order_id bigint;
    v_total numeric := 0;
    v_item jsonb;
    v_transaction_id bigint;
    v_balance numeric;
begin
    -- Calculate total
    for v_item in select * from jsonb_array_elements(p_items)
    loop
        v_total := v_total +
            ((v_item->>'quantity')::numeric * (v_item->>'sell_price')::numeric);
    end loop;

    -- Insert order
    insert into orders (
        customer_id, created_by, order_date, status,
        total_amount, delivery_price, delivery_type
    )
    values (
        p_customer_id, p_created_by, p_order_date, p_status,
        v_total, p_delivery_price, p_delivery_type
    )
    returning id into v_order_id;

    -- Insert items
    for v_item in select * from jsonb_array_elements(p_items)
    loop
        insert into order_items (
            order_id, product_id, quantity, buy_price, sell_price
        ) values (
            v_order_id,
            (v_item->>'product_id')::bigint,
            (v_item->>'quantity')::numeric,
            (v_item->>'buy_price')::numeric,
            (v_item->>'sell_price')::numeric
        );
    end loop;

    -- Deduct stock (negative allowed)
    if p_status in ('paid', 'delivered', 'picked up') then
        for v_item in select * from jsonb_array_elements(p_items)
        loop
            update products
            set stock = stock - (v_item->>'quantity')::numeric
            where id = (v_item->>'product_id')::bigint;
        end loop;
    end if;

    -- Apply cashflow
    if p_status in ('paid', 'delivered', 'picked up') then
        select ac.transaction_id, ac.current_balance
        into v_transaction_id, v_balance
        from apply_cash_inflow(
            p_created_by,
            v_order_id,
            v_total,
            p_delivery_price,
            p_order_date
        ) as ac;
    end if;

    -- return result
    order_id := v_order_id;
    transaction_id := v_transaction_id;
    current_balance := v_balance;

    return next;
end;
$$;
