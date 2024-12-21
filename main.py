# main.py
import time
import logging
from api_client import APIClient
from game_state import GameState, Snake
from decision_maker import DecisionMaker
from visualization import Visualization
from logger_config import setup_logger


def main():
    # Настройка логирования
    setup_logger()
    logging.info("Запуск бота для 3D Snake")

    # Конфигурация
    TOKEN = "YOUR_TOKEN_HERE"  # Замените на ваш токен
    SERVER_URL = "https://games-test.datsteam.dev"  # Используйте основной сервер для финальных раундов

    api_client = APIClient(token=TOKEN, server_url=SERVER_URL)
    decision_maker = DecisionMaker()

    # Получаем начальное состояние игры
    initial_game_state = api_client.get_game_state()
    if not initial_game_state or not initial_game_state.snakes:
        logging.error("Не удалось получить информацию о вашей змее.")
        return

    my_snake = initial_game_state.snakes[0]  # Если несколько, необходимо выбрать нужную
    logging.info(f"Управляется змеёй с ID: {my_snake.id}")

    while True:
        game_state = api_client.get_game_state()
        if not game_state:
            logging.error("Нет состояния игры, пробуем снова через 1 секунду.")
            time.sleep(1)
            continue

        # Проверка статуса вашей змеи
        my_snake = next((s for s in game_state.snakes if s.id == my_snake.id), my_snake)
        if my_snake.status == "dead":
            logging.info("Змея мертва, ожидаем возрождения.")
            time.sleep(game_state.revive_timeout_sec)
            continue

        # Принятие решения о движении
        direction = decision_maker.decide_move(game_state, my_snake)

        # Отправка команды о движении
        api_client.send_move(my_snake.id, direction)

        # Логика ожидания конца тика
        tick_time = game_state.tick_remain_ms / 1000.0  # Перевод в секунды
        logging.debug(f"Ожидание конца тика: {tick_time} секунд")
        time.sleep(tick_time)

        # Обновление состояния змеи после хода
        updated_game_state = api_client.get_game_state()
        if updated_game_state:
            my_snake = next(
                (s for s in updated_game_state.snakes if s.id == my_snake.id), my_snake
            )

        # Визуализация (опционально)
        # Uncomment the following lines to enable visualization
        # visualization = Visualization(updated_game_state, my_snake)
        # visualization.plot()


if __name__ == "__main__":
    main()
