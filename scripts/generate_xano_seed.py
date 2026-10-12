"""Gera uma massa determinística compatível com o schema Xano versionado.

O script não cria colunas de negócio que não existem no workspace atual.
Execute na raiz do projeto:

    python scripts/generate_xano_seed.py

Use --vendedor-id para apontar para um usuário já existente no Xano.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "seed_xano"
RANDOM_SEED = 20261012

VEHICLE_IMAGES = [
    "https://http2.mlstatic.com/D_NQ_NP_674749-MLB114249648383_072026-O.webp",
    "https://s2-autoesporte.glbimg.com/G0aevXvsJ8RofuqVWsMi2inlNZg=/432x395:3599x2620/1008x0/smart/filters:strip_icc()/i.s3.glbimg.com/v1/AUTH_59edd422c0c84a879bd37670ae4f538a/internal_photos/bs/2019/i/e/eNXrUaSEA8fsE564E2aw/img-20190904-135143-1-.jpg",
    "https://img1.icarros.com/dbimg/galeriaimgmodelo/2/134905_1.jpg",
    "https://midiawm1.webmotors.com.br/wp-content/uploads/2023/02/12225213/Honda-Civic-10a-geracao-2-scaled.webp",
    "https://autobusiness.com.br/_next/image?url=https%3A%2F%2Fs3.carro57.com.br%2FFC%2F2495%2F6783832_0_W_c7ce42f902.jpeg&w=828&q=100",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRFTZ3WlFkQYW9D4c2lpa75PcDAW3xbY263-wXdaq2nrvSBkF_cMW0ZLzI&s=10",
    "https://s3.ecompletocarros.dev/images/lojas/375/veiculos/167471/veiculoInfoVeiculoImagesMobile/vehicle_image_1699281238_d41d8cd98f00b204e9800998ecf8427e.jpeg",
    "https://cdn.motor1.com/images/mgl/pqge0/s3/novo-onix-premier-1.jpg",
    "https://cdn.wheel-size.com/automobile/body/chevrolet-sonic-2012-2016-1647408158.3455677.jpg",
    "https://www.automaistv.com.br/wp-content/uploads/2024/08/BYD-Song-Pro-8-1320x792.webp",
]

VEHICLE_CATALOG = [
    ("Honda", "Fit", 2015, 48900.00, VEHICLE_IMAGES[0]),
    ("Toyota", "Corolla Hybrid", 2020, 124900.00, VEHICLE_IMAGES[1]),
    ("Renault", "Kwid", 2020, 52900.00, VEHICLE_IMAGES[2]),
    ("Honda", "Civic", 2017, 96900.00, VEHICLE_IMAGES[3]),
    ("Hyundai", "Tucson", 2015, 79900.00, VEHICLE_IMAGES[4]),
    ("Fiat", "Mobi", 2026, 75900.00, VEHICLE_IMAGES[5]),
    ("Nissan", "Sentra", 2015, 69900.00, VEHICLE_IMAGES[6]),
    ("Chevrolet", "Onix", 2020, 68900.00, VEHICLE_IMAGES[7]),
    ("Chevrolet", "Sonic", 2016, 57900.00, VEHICLE_IMAGES[8]),
    ("BYD", "Song Pro", 2024, 189900.00, VEHICLE_IMAGES[9]),
]

FIRST_NAMES = [
    "Ana", "Bruno", "Camila", "Daniel", "Eduarda", "Felipe", "Gabriela",
    "Henrique", "Isabela", "Joao", "Karina", "Lucas", "Mariana", "Nicolas",
    "Olivia", "Paulo", "Rafaela", "Sergio", "Tatiane", "Vinicius",
]
LAST_NAMES = [
    "Almeida", "Barbosa", "Cardoso", "Dias", "Ferreira", "Gomes", "Lima",
    "Mendes", "Nogueira", "Oliveira", "Pereira", "Ramos", "Santos", "Silva",
    "Souza", "Teixeira", "Vieira", "Costa", "Martins", "Rocha",
]


def money(value: Decimal | float) -> float:
    return float(Decimal(str(value)).quantize(Decimal("0.01")))


def cpf(number: int) -> str:
    digits = f"{number:09d}"
    first = sum(int(digit) * (10 - index) for index, digit in enumerate(digits))
    first_digit = 0 if first % 11 < 2 else 11 - first % 11
    second_base = digits + str(first_digit)
    second = sum(int(digit) * (11 - index) for index, digit in enumerate(second_base))
    second_digit = 0 if second % 11 < 2 else 11 - second % 11
    complete = second_base + str(second_digit)
    return f"{complete[:3]}.{complete[3:6]}.{complete[6:9]}-{complete[9:]}"


def fixed_records() -> dict[str, list[dict[str, Any]]]:
    return {
        "status_veiculo": [
            {"id": 1, "Descricao": "Disponível"},
            {"id": 2, "Descricao": "Vendido"},
            {"id": 3, "Descricao": "Reservado"},
        ],
        "status_venda": [
            {"id": 1, "Descricao_venda": "Pendente"},
            {"id": 2, "Descricao_venda": "Concluída"},
            {"id": 3, "Descricao_venda": "Cancelada"},
        ],
        "forma_pagamento": [
            {"id": 1, "Metodo": "Financiamento Bancário"},
            {"id": 2, "Metodo": "PIX"},
            {"id": 3, "Metodo": "Cartão de Crédito"},
            {"id": 4, "Metodo": "Boleto Bancário"},
            {"id": 5, "Metodo": "Consórcio"},
        ],
        "veiculo_area": [
            {"id": 1, "Secao": "Revisão e Óleos"},
            {"id": 2, "Secao": "Freios e Suspensão"},
            {"id": 3, "Secao": "Acessórios e Estética"},
            {"id": 4, "Secao": "Elétrica e Baterias"},
            {"id": 5, "Secao": "Lataria e Funilaria"},
        ],
        "perfil": [
            {"id": 1, "Cargo": "Vendedor"},
        ],
        "veiculo": [
            {
                "id": index,
                "Marca": brand,
                "Modelo": model,
                "Cor": ["Prata", "Branco", "Preto", "Cinza"][index % 4],
                "Ano": year,
                "Placa": f"SEED{index:04d}",
                "Chassi": f"9BWSEED2026{index:05d}",
                "Quilometragem": 12000 + index * 7300,
                "Preco": price,
                "status_id": 1,
                "imagem_url": image,
            }
            for index, (brand, model, year, price, image) in enumerate(VEHICLE_CATALOG, 1)
        ],
        "peca": [
            {"id": 1, "PCNome": "Kit óleo Honda", "PCvalor": 289.90, "qtd_disp": 40, "area_id": 1},
            {"id": 2, "PCNome": "Óleo sintético Toyota", "PCvalor": 319.90, "qtd_disp": 35, "area_id": 1},
            {"id": 3, "PCNome": "Pastilha de freio Civic", "PCvalor": 459.90, "qtd_disp": 25, "area_id": 2},
            {"id": 4, "PCNome": "Pastilha de freio Onix", "PCvalor": 239.90, "qtd_disp": 30, "area_id": 2},
            {"id": 5, "PCNome": "Amortecedor Tucson", "PCvalor": 689.90, "qtd_disp": 16, "area_id": 2},
            {"id": 6, "PCNome": "Tapete premium Corolla", "PCvalor": 249.90, "qtd_disp": 22, "area_id": 3},
            {"id": 7, "PCNome": "Kit estética automotiva", "PCvalor": 179.90, "qtd_disp": 45, "area_id": 3},
            {"id": 8, "PCNome": "Carregador BYD Wallbox", "PCvalor": 4290.00, "qtd_disp": 8, "area_id": 4},
            {"id": 9, "PCNome": "Bateria 60Ah Mobi", "PCvalor": 599.90, "qtd_disp": 18, "area_id": 4},
            {"id": 10, "PCNome": "Lanterna traseira Kwid", "PCvalor": 389.90, "qtd_disp": 12, "area_id": 5},
        ],
    }


def generate_clients() -> list[dict[str, Any]]:
    records = []
    for index in range(1, 101):
        first = FIRST_NAMES[(index - 1) % len(FIRST_NAMES)]
        last = LAST_NAMES[((index - 1) // len(FIRST_NAMES)) % len(LAST_NAMES)]
        name = f"{first} {last}"
        records.append({
            "id": index,
            "CNome": name,
            "CPF": cpf(100000000 + index * 7919),
            "Telefone": f"+55 11 9{index:08d}",
            "Email": f"cliente{index:03d}@exemplo.com.br",
        })
    return records


def generate_transactions(
    clients: list[dict[str, Any]],
    fixed: dict[str, list[dict[str, Any]]],
    vendedor_id: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    rng = random.Random(RANDOM_SEED)
    vehicles = fixed["veiculo"]
    parts = fixed["peca"]
    now = datetime.now(timezone.utc)
    sales = []
    items = []
    installments = []
    item_id = 1
    for sale_id in range(1, 101):
        is_vehicle = sale_id <= 35
        if is_vehicle:
            vehicle = vehicles[(sale_id - 1) % len(vehicles)]
            rows = [(vehicle["id"], None, 1, vehicle["Preco"])]
            payment_id = rng.choice([1, 1, 5, 5, 2])
        else:
            count = 1 + (sale_id % 3)
            rows = []
            for offset in range(count):
                part = parts[(sale_id + offset) % len(parts)]
                rows.append((None, part["id"], 1 + (sale_id + offset) % 2, part["PCvalor"]))
            payment_id = rng.choice([2, 2, 3, 3, 4])
        total = money(sum(Decimal(str(row[3])) * row[2] for row in rows))
        sold_at = now - timedelta(days=rng.randint(0, 299), hours=rng.randint(0, 23))
        sales.append({
            "id": sale_id,
            "cliente_id": clients[(sale_id - 1) % len(clients)]["id"],
            "vendedor_id": vendedor_id,
            "forma_pagamento_id": payment_id,
            "status_id": 2,
            "Valor_bruto": total,
            "Desconto": 0.0,
            "Valor_final": total,
            "data_venda": sold_at.isoformat().replace("+00:00", "Z"),
        })
        for vehicle_id, part_id, quantity, unit_price in rows:
            items.append({
                "id": item_id,
                "venda_id": sale_id,
                "veiculo_id": vehicle_id,
                "peca_id": part_id,
                "qtd": quantity,
                "preco_unit": money(unit_price),
            })
            item_id += 1
        installments.append({
            "id": sale_id,
            "venda_id": sale_id,
            "numero_parcela": 1,
            "total_parcelas": 1,
            "valor": total,
            "vencimento": sold_at.isoformat().replace("+00:00", "Z"),
            "status": "RECEBIDA",
            "forma_recebida_id": payment_id,
            "recebido_em": sold_at.isoformat().replace("+00:00", "Z"),
        })
    return sales, items, installments


def write_records(output: Path, name: str, records: list[dict[str, Any]]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / f"{name}.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_csv(output: Path, name: str, records: list[dict[str, Any]]) -> None:
    if not records:
        return
    with (output / f"{name}.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--vendedor-id", type=int, default=1)
    args = parser.parse_args()

    fixed = fixed_records()
    clients = generate_clients()
    sales, items, installments = generate_transactions(clients, fixed, args.vendedor_id)
    all_records = {
        **fixed,
        "cliente": clients,
        "venda": sales,
        "venda_item": items,
        "venda_parcela": installments,
    }
    for name, records in all_records.items():
        write_records(args.output, name, records)
    for name in ("status_veiculo", "status_venda", "forma_pagamento", "veiculo_area", "perfil", "veiculo", "peca"):
        write_csv(args.output, name, fixed[name])
    write_csv(args.output, "cliente", clients)
    write_csv(args.output, "venda", sales)
    write_csv(args.output, "venda_item", items)
    write_csv(args.output, "venda_parcela", installments)
    print(f"Seed Xano gerado em {args.output}")


if __name__ == "__main__":
    main()
