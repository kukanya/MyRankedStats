-- phpMyAdmin SQL Dump
-- version 4.5.1
-- http://www.phpmyadmin.net
--
-- Хост: 127.0.0.1
-- Время создания: Янв 30 2016 г., 15:53
-- Версия сервера: 10.1.9-MariaDB
-- Версия PHP: 5.6.15

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База данных: `myrankedstats`
--

-- --------------------------------------------------------

--
-- Структура таблицы `champions`
--

CREATE TABLE `champions` (
  `championId` int(10) NOT NULL,
  `name` varchar(50) NOT NULL,
  `title` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Структура таблицы `matches`
--

CREATE TABLE `matches` (
  `summonerRegion` varchar(5) NOT NULL,
  `summonerId` int(20) NOT NULL,
  `region` varchar(5) NOT NULL,
  `matchId` bigint(15) NOT NULL,
  `timestamp` bigint(20) NOT NULL,
  `season` varchar(20) NOT NULL,
  `championId` int(10) NOT NULL,
  `role` varchar(20) NOT NULL,
  `winner` tinyint(1) NOT NULL,
  `kills` int(4) NOT NULL,
  `deaths` int(4) NOT NULL,
  `assists` int(4) NOT NULL,
  `primaryOpponent` int(10) DEFAULT NULL,
  `secondaryOpponent` int(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Структура таблицы `meta`
--

CREATE TABLE `meta` (
  `version` varchar(20) NOT NULL,
  `seasons` varchar(200) NOT NULL,
  `queues` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Дамп данных таблицы `meta`
--

INSERT INTO `meta` (`version`, `seasons`, `queues`) VALUES
('None', 'SEASON2015,PRESEASON2016,SEASON2016', 'RANKED_SOLO_5x5,TEAM_BUILDER_DRAFT_RANKED_5x5');

-- --------------------------------------------------------

--
-- Структура таблицы `summoners`
--

CREATE TABLE `summoners` (
  `region` varchar(5) NOT NULL,
  `summonerId` int(20) NOT NULL,
  `name` varchar(30) NOT NULL,
  `timestamp` bigint(20) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `champions`
--
ALTER TABLE `champions`
  ADD PRIMARY KEY (`championId`);

--
-- Индексы таблицы `matches`
--
ALTER TABLE `matches`
  ADD PRIMARY KEY (`summonerRegion`,`summonerId`,`region`,`matchId`),
  ADD KEY `championId` (`championId`),
  ADD KEY `summonerRegion` (`summonerRegion`,`summonerId`),
  ADD KEY `primaryOpponent` (`primaryOpponent`,`secondaryOpponent`),
  ADD KEY `secondaryOpponent` (`secondaryOpponent`);

--
-- Индексы таблицы `meta`
--
ALTER TABLE `meta`
  ADD PRIMARY KEY (`version`);

--
-- Индексы таблицы `summoners`
--
ALTER TABLE `summoners`
  ADD PRIMARY KEY (`region`,`summonerId`);

--
-- Ограничения внешнего ключа сохраненных таблиц
--

--
-- Ограничения внешнего ключа таблицы `matches`
--
ALTER TABLE `matches`
  ADD CONSTRAINT `matches_ibfk_1` FOREIGN KEY (`championId`) REFERENCES `champions` (`championId`) ON UPDATE CASCADE,
  ADD CONSTRAINT `matches_ibfk_2` FOREIGN KEY (`summonerRegion`,`summonerId`) REFERENCES `summoners` (`region`, `summonerId`) ON UPDATE CASCADE,
  ADD CONSTRAINT `matches_ibfk_3` FOREIGN KEY (`primaryOpponent`) REFERENCES `champions` (`championId`) ON UPDATE CASCADE,
  ADD CONSTRAINT `matches_ibfk_4` FOREIGN KEY (`secondaryOpponent`) REFERENCES `champions` (`championId`) ON UPDATE CASCADE;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
