
create or replace function update_order_full(
    p_order_id bigint,
    p_customer_id bigint,
    p_created_by uuid,
    p_order_date timestamptz,
    p_status text,
    p_delivery_price numeric,
    p_delivery_type text,
    p_items jsonb,
    p_items_to_delete bigint[]
)
returns table (
    out_order_id bigint,
    out_transaction_id bigint,
    out_current_balance numeric
)
language plpgsql
as $$
declare
    v_old_status text;
    v_total numeric := 0;
    v_item jsonb;
    v_transaction_id bigint;
    v_balance numeric;
begin
    -- Get old status
    select status into v_old_status
    from orders
    where id = p_order_id;

    if not found then
        raise exception 'Order not found';
    end if;

    -- Calculate total
    for v_item in select * from jsonb_array_elements(p_items)
    loop
        v_total := v_total +
            ((v_item->>'quantity')::numeric * (v_item->>'sell_price')::numeric);
    end loop;

    -- Update order
    update orders
    set customer_id = p_customer_id,
        order_date = p_order_date,
        status = p_status,
        total_amount = v_total,
        delivery_price = p_delivery_price,
        delivery_type = p_delivery_type
    where id = p_order_id;

    -- Delete removed items
    if p_items_to_delete is not null then
        delete from order_items
        where id = any(p_items_to_delete)
        and order_id = p_order_id;
    end if;

    -- Upsert items
    for v_item in select * from jsonb_array_elements(p_items)
    loop
        if (v_item ? 'id') then
            update order_items
            set product_id = (v_item->>'product_id')::bigint,
                quantity = (v_item->>'quantity')::numeric,
                buy_price = (v_item->>'buy_price')::numeric,
                sell_price = (v_item->>'sell_price')::numeric
            where id = (v_item->>'id')::bigint
              and order_id = p_order_id;
        else
            insert into order_items (
                order_id, product_id, quantity, buy_price, sell_price
            ) values (
                p_order_id,
                (v_item->>'product_id')::bigint,
                (v_item->>'quantity')::numeric,
                (v_item->>'buy_price')::numeric,
                (v_item->>'sell_price')::numeric
            );
        end if;
    end loop;

    -- Deduct stock (negative allowed)
    if p_status in ('delivered', 'picked up') then
        for v_item in select * from jsonb_array_elements(p_items)
        loop
            update products
            set stock = stock - (v_item->>'quantity')::numeric
            where id = (v_item->>'product_id')::bigint;
        end loop;
    end if;

    -- Apply cashflow on first transition
    if v_old_status not in ('paid', 'delivered', 'picked up')
       and p_status in ('paid', 'delivered', 'picked up') then

        select transaction_id, current_balance
        into v_transaction_id, v_balance
        from apply_cash_inflow(
            p_created_by,
            p_order_id,
            v_total,
            p_delivery_price,
            p_order_date
        );
    end if;

    -- Return result
    out_order_id := p_order_id;
    out_transaction_id := v_transaction_id;
    out_current_balance := v_balance;

    return next;
end;
$$;
