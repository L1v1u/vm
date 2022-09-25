import json
from flask import url_for
from collections import namedtuple
from vm.extensions import pwd_context
from vm.models import User, Role


def get_current_user_token(client, user):
    data = {
        'username': user.username,
        'password': "stringString2",
    }

    rep = client.post(
        '/auth/login',
        data=json.dumps(data),
        headers={'content-type': 'application/json'}
    )

    tokens = json.loads(rep.get_data(as_text=True))

    return {
        'content-type': 'application/json',
        'authorization': 'Bearer %s' % tokens['access_token']
    }


def test_get_user(client, db, user):
    # test 401
    user_url = url_for('api.user_by_id', user_id="100000")
    rep = client.get(user_url, headers={})
    assert rep.status_code == 401

    db.session.add(user)
    db.session.commit()

    current_user_headers = get_current_user_token(client, user)

    # test get_user
    user_url = url_for('api.user_by_id', user_id=user.id)
    rep = client.get(user_url, headers=current_user_headers)
    assert rep.status_code == 200

    data = rep.get_json()["user"]
    assert data["username"] == user.username
    assert data["active"] == user.active


def test_put_user(client, db, user):
    # test 401
    user_url = url_for('api.user_by_id', user_id="100000")
    rep = client.put(user_url)
    assert rep.status_code == 401

    db.session.add(user)
    db.session.commit()

    # test update user validation error for password not matching regexp
    data = {"username": "updated", "password": "123p"}
    user_url = url_for('api.user_by_id', user_id=user.id)

    current_user_headers = get_current_user_token(client, user)
    rep = client.put(user_url, json=data, headers=current_user_headers)
    assert rep.status_code == 400

    # test update user validation passed for password
    data = {"username": "updated", "password": "stringString2"}

    rep = client.put(user_url, json=data, headers=current_user_headers)
    assert rep.status_code == 201

    data = rep.get_json()["user"]
    assert data["username"] == "updated"
    assert data["active"] == user.active

    db.session.refresh(user)
    assert pwd_context.verify("stringString2", user.password)


def test_delete_user(client, db, user):
    # test 401
    user_url = url_for('api.user_by_id', user_id="100000")
    rep = client.delete(user_url)
    assert rep.status_code == 401

    db.session.add(user)
    db.session.commit()

    # test get_user
    current_user_headers = get_current_user_token(client, user)

    user_url = url_for('api.user_by_id', user_id=user.id)
    rep = client.delete(user_url,  headers=current_user_headers)
    assert rep.status_code == 200
    assert db.session.query(User).filter_by(id=user.id).first() is None


def test_create_user(client, db):
    # test bad data
    users_url = url_for('api.users')
    role_seller = Role(id=3, name="SELLER")
    db.session.add(role_seller)

    data = {"username": "created",
            "role_name": "SELLER",
            "password": "admin"}

    rep = client.post(users_url, json=data)
    assert rep.status_code == 400

    # password to pass validation
    data['password'] = 'stringString2'
    rep = client.post(users_url, json=data)
    assert rep.status_code == 201

    data = rep.get_json()
    user = db.session.query(User).filter_by(id=data["user"]["id"]).first()

    assert user.username == "created"


def test_deposit(client, db):
    deposit_url = url_for('api.deposit')
    users_url = url_for('api.users')
    role_buyer = Role(id=2, name="BUYER")
    db.session.add(role_buyer)

    data = {"username": "created",
            "role_name": "BUYER",
            "password": "stringString2"}

    rep = client.post(users_url, json=data)
    data = rep.get_json()


    d_named = namedtuple('Struct', data['user'].keys())(*data['user'].values())

    current_user_headers = get_current_user_token(client, d_named)

    data = {"deposit": 13}
    rep = client.post(deposit_url, json=data, headers=current_user_headers)
    assert rep.status_code == 400

    data = {"deposit": 20}
    rep = client.post(deposit_url, json=data, headers=current_user_headers)
    assert rep.status_code == 201


def test_buy(client, db):

    users_url = url_for('api.users')
    buy_url = url_for('api.buy')
    product_create_url = url_for('api.products')
    deposit_url = url_for('api.deposit')

    role_buyer = Role(id=1, name="BUYER")
    role_seller = Role(id=2, name="SELLER")
    db.session.add(role_seller)
    db.session.add(role_buyer)

    rep = client.post(users_url, json={"username": "buyer",
            "role_name": "BUYER",
            "password": "stringString2"})
    data_buyer = rep.get_json()

    rep = client.post(users_url, json={"username": "seller",
            "role_name": "SELLER",
            "password": "stringString2"})
    data_seller = rep.get_json()

    d_seller = namedtuple('Struct', data_seller['user'].keys())(*data_seller['user'].values())
    d_buyer = namedtuple('Struct', data_buyer['user'].keys())(*data_buyer['user'].values())

    current_user_headers_seller = get_current_user_token(client, d_seller)
    current_user_headers_buyer = get_current_user_token(client, d_buyer)

    resp = client.post(product_create_url,
                       json={
                          "amount_available": 10,
                          "cost": 10,
                          "product_name": "test product"
                        },
                       headers=current_user_headers_seller)

    data_resp_prod = resp.get_json()

    data = {"deposit": 20}
    client.post(deposit_url, json=data, headers=current_user_headers_buyer)

    data = {"deposit": 50}
    client.post(deposit_url, json=data, headers=current_user_headers_buyer)

    data = {"deposit": 5}
    client.post(deposit_url, json=data, headers=current_user_headers_buyer)

    resp = client.post(buy_url,
                       json=[{
                                    "amount_to_buy": 1,
                                    "id": data_resp_prod['Product']['id']
                             }],
                       headers=current_user_headers_buyer)
    data = resp.get_json()
    assert data['msg'] == "Order created"
    assert resp.status_code == 201
    assert data['change_to_return'] == {'100': 0, '50': 1, '20': 0, '10': 1, '5': 1}







