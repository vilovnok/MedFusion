from tasks import generate_task, number_test_task, number_topic_task

generate_task.delay("Тестовое содержимое")
number_test_task.delay("Тестовое содержимое")
number_topic_task.delay("Тестовое содержимое")